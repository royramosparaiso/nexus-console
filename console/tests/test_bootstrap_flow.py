"""End-to-end bootstrap: Console signs, mock Platform verifies, DB updated."""

from __future__ import annotations

import asyncio
import time
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from starlette.requests import Request as StarletteRequest

from nexus_core.contracts.bootstrap import (
    BootstrapRequest, BootstrapResponse, BootstrapStatus,
)
from nexus_core.contracts.commands import CommandKind
from nexus_core.contracts.notifications import (
    Notification, NotificationEnvelope, NotificationKind, NotificationStatus,
)
from nexus_core.jwt import PlatformKeypair, sign_notification, verify_token

from app.models.db import InstanceRow
from app.services.bootstrap_client import dispatch_bootstrap
from app.services.keypair import get_or_create_keypair
from app.services.manifest import submission_to_manifest
from app.models.wizard import WizardSubmission


def _sub() -> WizardSubmission:
    return WizardSubmission.model_validate({
        "instance_name": "acme-e2e",
        "persona": {"display_name": "Acme", "kind": "company", "description": "", "default_locale": "en-US"},
        "deployment": {"modality": "local", "tls": True, "autoscale": False},
        "llms": {
            "enabled_providers": ["ollama"],
            "roles": {"planner": "llama3.1:70b", "coordinator": "llama3.1:8b",
                       "worker": "llama3.1:8b", "embeddings": "nomic-embed-text"},
            "allow_fallback": True, "monthly_budget_usd": 0.0,
        },
        "memory": {"driver": "sqlite", "graph": "none",
                    "retention_days": 365, "encryption_at_rest": True},
        "areas": {"enabled": ["personal_organization", "meetings"]},
        "governance": {"default_autonomy": "act_with_approval", "kill_switch_enabled": True,
                        "audit_retention_days": 730, "monthly_budget_alert_pct": 80,
                        "require_2fa_for_superadmin": True},
    })


class _MockPlatform:
    """In-process ASGI app mimicking Platform /_bootstrap + /_commands."""

    def __init__(self):
        self.keypair = PlatformKeypair.generate()
        self.console_pubkey: str | None = None
        self.received_manifest = None
        self.commands_received: list[str] = []

        app = FastAPI()

        @app.get("/_health")
        async def _h():
            return {"status": "ok"}

        @app.post("/_bootstrap")
        async def _boot(req: dict):
            request = BootstrapRequest.model_validate(req)
            self.console_pubkey = request.console_public_key_pem
            self.received_manifest = request.manifest
            return BootstrapResponse(
                status=BootstrapStatus.OK,
                platform_public_key_pem=self.keypair.public_pem(),
                platform_version="0.6.0",
                applied_areas=list(request.manifest.areas.enabled),
            ).model_dump(mode="json")

        @app.post("/_commands")
        async def _cmd(request: StarletteRequest):
            body = await request.body()
            payload = verify_token(body.decode(), self.console_pubkey)
            self.commands_received.append(payload["command"]["kind"])
            # The real Platform dispatcher applies synchronously and returns
            # APPLIED. Match that contract so the Console’s command log ends
            # in a terminal state.
            return {"cmd_id": payload["cmd_id"], "status": "applied", "detail": None}

        self.app = app


async def test_full_bootstrap_and_command_roundtrip(client, session_factory):
    mock = _MockPlatform()
    transport = httpx.ASGITransport(app=mock.app)

    # 1. Submit wizard in dry_run mode so the background deployer doesn't run.
    r = await client.post("/wizard/submit?dry_run=true", json=_sub().model_dump(mode="json"))
    assert r.status_code == 200
    iid = r.json()["instance_id"]

    # 2. Manually invoke dispatch_bootstrap with the mock as the http client.
    async with session_factory() as db:
        row = await db.get(InstanceRow, iid)
        assert row is not None
        assert row.bootstrap_token
        kp = await get_or_create_keypair(db)
        manifest = submission_to_manifest(_sub())

        async with httpx.AsyncClient(transport=transport, base_url="http://mock-platform") as http:
            resp = await dispatch_bootstrap(
                db=db, row=row,
                endpoint="http://mock-platform",
                token=row.bootstrap_token,
                console_kp=kp, manifest=manifest,
                webhook_url="http://console:7000/_platform/notify",
                http_client=http,
            )

        assert resp.status == BootstrapStatus.OK
        await db.refresh(row)
        assert row.status == "running"
        assert row.bootstrap_token is None
        assert row.platform_public_key_pem == mock.keypair.public_pem()

    # 3. Mock received the correct manifest
    assert mock.received_manifest.name == "acme-e2e"

    # 4. Send a signed command through the API.
    #    We patch httpx.AsyncClient inside instances.py to route to the mock.
    import app.api.instances as instances_mod

    original = instances_mod.httpx.AsyncClient

    def _factory(*args, **kwargs):
        return original(transport=transport, base_url="http://mock-platform")

    instances_mod.httpx.AsyncClient = _factory
    try:
        r = await client.post(
            f"/instances/{iid}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {"name": "clients"}},
        )
        assert r.status_code == 202, r.text
        body = r.json()
        assert body["status"] == "queued"
        assert body["accepted"] is True
        cmd_id = body["cmd_id"]

        # Background task dispatches asynchronously — poll until the mock
        # actually receives the command.
        for _ in range(50):
            if mock.commands_received:
                break
            await asyncio.sleep(0.02)

        # Poll the status endpoint until the command reaches a terminal state.
        terminal = {"applied", "failed", "rejected"}
        final_status = None
        for _ in range(100):
            sr = await client.get(f"/instances/{iid}/commands/{cmd_id}")
            assert sr.status_code == 200, sr.text
            final_status = sr.json()["status"]
            if final_status in terminal:
                break
            await asyncio.sleep(0.02)
        assert final_status == "applied", final_status
    finally:
        instances_mod.httpx.AsyncClient = original

    assert mock.commands_received == [CommandKind.CREATE_SPACE.value]


async def test_platform_notify_verifies_signature(client, session_factory):
    """After bootstrap, Platform can push signed notifications back to Console."""
    mock = _MockPlatform()
    transport = httpx.ASGITransport(app=mock.app)

    r = await client.post("/wizard/submit?dry_run=true", json=_sub().model_dump(mode="json"))
    iid = r.json()["instance_id"]

    async with session_factory() as db:
        row = await db.get(InstanceRow, iid)
        kp = await get_or_create_keypair(db)
        manifest = submission_to_manifest(_sub())
        async with httpx.AsyncClient(transport=transport, base_url="http://mock-platform") as http:
            await dispatch_bootstrap(
                db=db, row=row, endpoint="http://mock-platform",
                token=row.bootstrap_token, console_kp=kp, manifest=manifest,
                webhook_url="http://console:7000/_platform/notify",
                http_client=http,
            )

    from uuid import UUID
    now = int(time.time())
    env = NotificationEnvelope(
        instance_id=UUID(iid),
        issued_at=now,
        expires_at=now + 300,
        notification=Notification(
            kind=NotificationKind.HEALTH_HEARTBEAT,
            payload={"cpu_pct": 12.4, "mem_pct": 34.1},
        ),
    )
    token = sign_notification(mock.keypair, env)

    r = await client.post("/_platform/notify", content=token, headers={"Content-Type": "application/jwt"})
    assert r.status_code == 200
    assert r.json()["status"] == NotificationStatus.ACK.value


async def test_platform_notify_rejects_bad_signature(client, session_factory):
    mock = _MockPlatform()
    imposter = PlatformKeypair.generate()
    transport = httpx.ASGITransport(app=mock.app)

    r = await client.post("/wizard/submit?dry_run=true", json=_sub().model_dump(mode="json"))
    iid = r.json()["instance_id"]

    async with session_factory() as db:
        row = await db.get(InstanceRow, iid)
        kp = await get_or_create_keypair(db)
        manifest = submission_to_manifest(_sub())
        async with httpx.AsyncClient(transport=transport, base_url="http://mock-platform") as http:
            await dispatch_bootstrap(
                db=db, row=row, endpoint="http://mock-platform",
                token=row.bootstrap_token, console_kp=kp, manifest=manifest,
                webhook_url="http://console:7000/_platform/notify",
                http_client=http,
            )

    from uuid import UUID
    now = int(time.time())
    env = NotificationEnvelope(
        instance_id=UUID(iid),
        issued_at=now,
        expires_at=now + 300,
        notification=Notification(kind=NotificationKind.ERROR, payload={"msg": "boom"}),
    )
    token = sign_notification(imposter, env)  # signed by wrong key

    r = await client.post("/_platform/notify", content=token, headers={"Content-Type": "application/jwt"})
    assert r.status_code == 200
    assert r.json()["status"] == NotificationStatus.INVALID_SIGNATURE.value
