"""Tests for the optional Voicebox voice-sidecar integration."""

from __future__ import annotations

import pytest

import app.api.voicebox as vb
from app.core.config import settings


@pytest.fixture(autouse=True)
def _reset_voicebox_settings():
    """Snapshot + restore the global settings the voicebox API reads."""
    keys = (
        "voicebox_enabled",
        "voicebox_base_url",
        "voicebox_api_key",
        "voicebox_mcp_path",
        "voicebox_voice_cloning_consent",
    )
    saved = {k: getattr(settings, k) for k in keys}
    # Deterministic defaults for each test.
    settings.voicebox_enabled = False
    settings.voicebox_base_url = None
    settings.voicebox_api_key = None
    settings.voicebox_mcp_path = "/mcp"
    settings.voicebox_voice_cloning_consent = False
    yield
    for k, v in saved.items():
        setattr(settings, k, v)


# ---------------------------------------------------------------------------
# config — redaction + derived fields
# ---------------------------------------------------------------------------

async def test_config_disabled_by_default(client) -> None:
    resp = await client.get("/voicebox/config")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["configured"] is False
    assert body["api_key_configured"] is False
    assert body["mcp_url"] is None


async def test_config_redacts_api_key(client) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "http://localhost:5111"
    settings.voicebox_api_key = "super-secret-value"
    resp = await client.get("/voicebox/config")
    body = resp.json()
    assert body["api_key_configured"] is True
    assert body["configured"] is True
    assert body["mcp_url"] == "http://localhost:5111/mcp"
    # The secret must never appear anywhere in the payload.
    assert "super-secret-value" not in resp.text


async def test_config_invalid_url_is_not_configured(client) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "not-a-url"
    resp = await client.get("/voicebox/config")
    body = resp.json()
    assert body["configured"] is False
    assert body["mcp_url"] is None


# ---------------------------------------------------------------------------
# status — typed states, never raises
# ---------------------------------------------------------------------------

async def test_status_disabled(client) -> None:
    resp = await client.get("/voicebox/status")
    assert resp.status_code == 200
    assert resp.json()["state"] == "disabled"


async def test_status_unconfigured(client) -> None:
    settings.voicebox_enabled = True
    resp = await client.get("/voicebox/status")
    assert resp.json()["state"] == "unconfigured"


async def test_status_invalid_url(client) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "ftp://nope"
    resp = await client.get("/voicebox/status")
    assert resp.json()["state"] == "invalid_url"


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc
        self.last_headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url, headers=None):
        self.last_headers = headers
        if self._exc is not None:
            raise self._exc
        return self._response


async def test_status_reachable(client, monkeypatch) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "http://localhost:5111"
    fake = _FakeClient(response=_FakeResponse(200, {"version": "1.2.3"}))
    monkeypatch.setattr(vb.httpx, "AsyncClient", lambda *a, **k: fake)
    resp = await client.get("/voicebox/status")
    body = resp.json()
    assert body["state"] == "reachable"
    assert body["version"] == "1.2.3"
    assert body["latency_ms"] is not None


async def test_status_sends_bearer_when_key_present(client, monkeypatch) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "http://localhost:5111"
    settings.voicebox_api_key = "k"
    fake = _FakeClient(response=_FakeResponse(200))
    monkeypatch.setattr(vb.httpx, "AsyncClient", lambda *a, **k: fake)
    await client.get("/voicebox/status")
    assert fake.last_headers.get("Authorization") == "Bearer k"


async def test_status_unreachable_on_http_error(client, monkeypatch) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "http://localhost:5111"
    fake = _FakeClient(exc=vb.httpx.ConnectError("refused"))
    monkeypatch.setattr(vb.httpx, "AsyncClient", lambda *a, **k: fake)
    resp = await client.get("/voicebox/status")
    assert resp.json()["state"] == "unreachable"


async def test_status_unreachable_on_5xx(client, monkeypatch) -> None:
    settings.voicebox_enabled = True
    settings.voicebox_base_url = "http://localhost:5111"
    fake = _FakeClient(response=_FakeResponse(503))
    monkeypatch.setattr(vb.httpx, "AsyncClient", lambda *a, **k: fake)
    resp = await client.get("/voicebox/status")
    assert resp.json()["state"] == "unreachable"


# ---------------------------------------------------------------------------
# cloning consent — opt-in
# ---------------------------------------------------------------------------

async def test_cloning_consent_defaults_off(client) -> None:
    resp = await client.get("/voicebox/cloning-consent")
    body = resp.json()
    assert body["consent"] is False
    assert "own" in body["notice"].lower()


async def test_cloning_consent_reflects_opt_in(client) -> None:
    settings.voicebox_voice_cloning_consent = True
    resp = await client.get("/voicebox/cloning-consent")
    assert resp.json()["consent"] is True
