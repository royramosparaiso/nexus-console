"""End-to-end tests for /wizard/{id}/complete-remote.

The endpoint is what an operator (or Cloud Cowork / OpenClaw) calls after
running the handoff playbook on a Fly/Hetzner deployment. It:

  1. Waits for /_health on the given endpoint.
  2. Signs a BootstrapRequest with the Console keypair.
  3. POSTs it to /_bootstrap on Platform with the one-time token.
  4. Flips the InstanceRow to `running` and burns the token.

We simulate Platform with an in-process ASGI app served through
httpx.MockTransport, so no real network is involved.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from app.models.db import InstanceRow
from app.services import bootstrap_client
from tests.test_wizard import SAMPLE_SUBMISSION


# ────────────────────────────────────────────────────────────────
# Fake Platform (mock transport)
# ────────────────────────────────────────────────────────────────

def _make_platform_kp() -> tuple[str, str]:
    """Return (private_pem, public_pem) for a fake Platform."""
    priv = Ed25519PrivateKey.generate()
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return priv_pem, pub_pem


class FakePlatform:
    """Fake Platform that answers /_health and /_bootstrap.

    Records the last bootstrap request so tests can assert on it.
    """
    def __init__(self, *, healthy_after: int = 0):
        _, self.public_pem = _make_platform_kp()
        self.health_calls = 0
        self.healthy_after = healthy_after
        self.last_bootstrap_body: dict | None = None
        self.last_bootstrap_token: str | None = None
        self.status_code_on_bootstrap = 200
        self.already_bootstrapped = False

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/_health":
            self.health_calls += 1
            if self.health_calls > self.healthy_after:
                return httpx.Response(200, json={"status": "ok", "version": "0.7.0"})
            return httpx.Response(503, json={"status": "starting"})

        if request.url.path == "/_bootstrap":
            self.last_bootstrap_token = request.headers.get("X-Bootstrap-Token")
            self.last_bootstrap_body = json.loads(request.content)
            if self.status_code_on_bootstrap != 200:
                return httpx.Response(
                    self.status_code_on_bootstrap,
                    json={"error": "simulated failure"},
                )
            status = "already_bootstrapped" if self.already_bootstrapped else "ok"
            return httpx.Response(200, json={
                "status": status,
                "platform_public_key_pem": self.public_pem,
                "platform_version": "0.7.0",
                "error_detail": None,
            })

        return httpx.Response(404, json={"error": f"unknown path {request.url.path}"})


@pytest.fixture
def fake_platform(monkeypatch):
    """Route all httpx.AsyncClient traffic through a fake Platform."""
    fp = FakePlatform()

    real_async_client = httpx.AsyncClient

    def _patched_async_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(fp.handler)
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(bootstrap_client.httpx, "AsyncClient", _patched_async_client)
    return fp


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────

async def _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch):
    """Run wizard/submit with modality=fly to get a `handoff-pending` row."""
    from app.core.config import settings
    monkeypatch.setattr(settings, "deployments_dir", tmp_path, raising=False)

    body = {**SAMPLE_SUBMISSION, "instance_name": "cr-test", "deployment": {
        **SAMPLE_SUBMISSION["deployment"], "modality": "fly",
        "region": "mad", "domain": "cr-test.example",
    }}
    r = await client.post("/wizard/submit?dry_run=true", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "handoff-pending", j
    return j["instance_id"]


# ────────────────────────────────────────────────────────────────
# Happy path
# ────────────────────────────────────────────────────────────────

async def test_complete_remote_happy_path(client, tmp_path, monkeypatch, fake_platform):
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 5},
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "running"
    assert j["endpoint"] == "http://platform.example:8001"
    assert j["platform_version"] == "0.7.0"
    assert j["error_detail"] is None

    # Fake Platform was really called
    assert fake_platform.health_calls >= 1
    assert fake_platform.last_bootstrap_body is not None
    assert fake_platform.last_bootstrap_body["instance_id"] == iid
    assert "manifest" in fake_platform.last_bootstrap_body
    assert fake_platform.last_bootstrap_token is not None
    # The endpoint override was propagated to the request URL (health calls)


async def test_complete_remote_burns_the_token(
    client, tmp_path, monkeypatch, fake_platform, session_factory,
):
    from uuid import UUID
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 5},
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "running"

    async with session_factory() as s:
        row = await s.get(InstanceRow, UUID(iid))
        assert row.status == "running"
        assert row.bootstrap_token is None, "token must be burned after success"
        assert row.platform_public_key_pem is not None
        assert row.platform_version == "0.7.0"
        assert row.bootstrapped_at is not None


async def test_complete_remote_waits_for_health(client, tmp_path, monkeypatch, fake_platform):
    """First few /_health calls return 503, then 200 — endpoint must poll."""
    fake_platform.healthy_after = 2
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 10},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "running"
    assert fake_platform.health_calls >= 3  # 2 failures + 1 success


# ────────────────────────────────────────────────────────────────
# Failure paths
# ────────────────────────────────────────────────────────────────

async def test_complete_remote_unknown_instance(client, fake_platform):
    r = await client.post(
        "/wizard/00000000-0000-0000-0000-000000000000/complete-remote",
        json={"endpoint": "http://x.example"},
    )
    assert r.status_code == 404


async def test_complete_remote_invalid_uuid(client, fake_platform):
    r = await client.post(
        "/wizard/not-a-uuid/complete-remote",
        json={"endpoint": "http://x.example"},
    )
    assert r.status_code == 400


async def test_complete_remote_wrong_status(
    client, tmp_path, monkeypatch, fake_platform, session_factory,
):
    """Cannot complete-remote a local (already-running) instance."""
    from uuid import UUID
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    # Simulate a burned/completed instance
    async with session_factory() as s:
        row = await s.get(InstanceRow, UUID(iid))
        row.status = "running"
        row.bootstrap_token = None
        await s.commit()

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://x.example"},
    )
    assert r.status_code == 409, r.text
    assert "status 'running'" in r.json()["detail"]


async def test_complete_remote_platform_returns_500(
    client, tmp_path, monkeypatch, fake_platform, session_factory,
):
    from uuid import UUID
    fake_platform.status_code_on_bootstrap = 500
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 5},
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "bootstrap-failed"
    assert "500" in (j["error_detail"] or "")

    # Row must still have the token so the operator can retry.
    async with session_factory() as s:
        row = await s.get(InstanceRow, UUID(iid))
        assert row.status == "bootstrap-failed"
        assert row.bootstrap_token is not None


async def test_complete_remote_retry_after_failure(
    client, tmp_path, monkeypatch, fake_platform,
):
    """After a bootstrap-failed status, a second call must succeed."""
    fake_platform.status_code_on_bootstrap = 500
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 5},
    )
    assert r.json()["status"] == "bootstrap-failed"

    # Now fix Platform and retry
    fake_platform.status_code_on_bootstrap = 200
    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": "http://platform.example:8001", "wait_timeout_s": 5},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "running"


async def test_complete_remote_endpoint_override(
    client, tmp_path, monkeypatch, fake_platform, session_factory,
):
    """If the operator passes a different endpoint, we persist and use it."""
    from uuid import UUID
    iid = await _create_fly_handoff_pending_instance(client, tmp_path, monkeypatch)

    override = "https://real-domain.example"
    r = await client.post(
        f"/wizard/{iid}/complete-remote",
        json={"endpoint": override, "wait_timeout_s": 5},
    )
    assert r.status_code == 200
    assert r.json()["endpoint"] == override

    async with session_factory() as s:
        row = await s.get(InstanceRow, UUID(iid))
        assert row.endpoint == override
