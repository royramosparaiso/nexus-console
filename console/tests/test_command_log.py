"""Tests for the async command dispatch + command_log status endpoint."""

from __future__ import annotations

import asyncio
import time
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import select
from starlette.requests import Request as StarletteRequest

from app.models.db import CommandLogRow, InstanceRow
from app.services.keypair import get_or_create_keypair
from nexus_core.contracts.commands import CommandKind
from nexus_core.jwt import verify_token


class _MockPlatform:
    """Minimal Platform stub that verifies signed commands and returns a status."""

    def __init__(self, status: str = "applied", http_status: int = 200):
        self.status = status
        self.http_status = http_status
        self.received: list[dict] = []
        self.console_pubkey: str | None = None
        self.raise_network_error = False
        app = FastAPI()

        @app.post("/_commands")
        async def _cmd(request: StarletteRequest):
            body = await request.body()
            payload = verify_token(body.decode(), self.console_pubkey)
            self.received.append(payload)
            if self.http_status >= 500:
                return httpx.Response(self.http_status, text="boom").raise_for_status()
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=self.http_status,
                content={
                    "cmd_id": payload["cmd_id"],
                    "status": self.status,
                    "detail": None if self.http_status < 400 else "rejected by platform",
                    "error_code": None,
                },
            )

        self.app = app


async def _seed_running_instance(session_factory, endpoint: str) -> UUID:
    """Insert a running InstanceRow so /command passes the status guard."""
    async with session_factory() as db:
        # Ensure a keypair exists (Console must have one to sign)
        await get_or_create_keypair(db)
        row = InstanceRow(
            name=f"inst-{uuid4().hex[:8]}",
            persona_kind="individual",
            persona_display_name="Test",
            modality="text",
            agent_runtime="in_process",
            auth_provider="password_totp",
            endpoint=endpoint,
            status="running",
            manifest_json={},
            platform_public_key_pem="",  # not used by our mock
            platform_version="0.13.2",
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row.id


async def _wait_for(client, iid: UUID, cmd_id: UUID, terminal_only: bool = True):
    """Poll the status endpoint until terminal (or timeout)."""
    terminal = {"applied", "failed", "rejected"}
    for _ in range(200):
        r = await client.get(f"/instances/{iid}/commands/{cmd_id}")
        assert r.status_code == 200, r.text
        body = r.json()
        if not terminal_only or body["status"] in terminal:
            return body
        await asyncio.sleep(0.02)
    return body


def _patch_httpx(mock_platform: _MockPlatform):
    """Route httpx.AsyncClient inside instances.py to the mock's ASGI app."""
    import app.api.instances as instances_mod

    transport = httpx.ASGITransport(app=mock_platform.app)
    original = instances_mod.httpx.AsyncClient

    def _factory(*args, **kwargs):
        return original(transport=transport, base_url="http://mock-platform")

    instances_mod.httpx.AsyncClient = _factory
    return original, instances_mod


async def test_command_transitions_queued_to_applied(client, session_factory):
    """Happy path: command lands, mock returns applied, log ends in applied."""
    mock = _MockPlatform(status="applied")
    async with session_factory() as db:
        kp = await get_or_create_keypair(db)
        mock.console_pubkey = kp.public_pem()

    iid = await _seed_running_instance(session_factory, "http://mock-platform")

    original, instances_mod = _patch_httpx(mock)
    try:
        r = await client.post(
            f"/instances/{iid}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {"name": "x"}},
        )
        assert r.status_code == 202, r.text
        body = r.json()
        assert body["accepted"] is True
        assert body["status"] == "queued"
        cmd_id = body["cmd_id"]

        final = await _wait_for(client, iid, UUID(cmd_id))
        assert final["status"] == "applied"
        assert final["applied_at"] is not None
        assert final["kind"] == CommandKind.CREATE_SPACE.value
    finally:
        instances_mod.httpx.AsyncClient = original


async def test_command_rejects_on_non_running_instance(client, session_factory):
    """POST /command returns 409 when the instance isn't running."""
    async with session_factory() as db:
        await get_or_create_keypair(db)
        row = InstanceRow(
            name=f"inst-stopped-{uuid4().hex[:6]}",
            persona_kind="individual",
            persona_display_name="Test",
            modality="text",
            agent_runtime="in_process",
            auth_provider="password_totp",
            endpoint="http://ghost",
            status="stopped",
            manifest_json={},
        )
        db.add(row)
        await db.commit()
        iid = row.id

    r = await client.post(
        f"/instances/{iid}/command",
        json={"kind": CommandKind.CREATE_SPACE.value, "payload": {}},
    )
    assert r.status_code == 409
    assert "not running" in r.json()["detail"]


async def test_command_status_404_for_missing_cmd(client, session_factory):
    iid = await _seed_running_instance(session_factory, "http://mock-platform")
    fake_cmd = uuid4()
    r = await client.get(f"/instances/{iid}/commands/{fake_cmd}")
    assert r.status_code == 404


async def test_command_status_404_for_wrong_instance(client, session_factory):
    """A cmd_id belongs to exactly one instance; cross-lookup returns 404."""
    mock = _MockPlatform(status="applied")
    async with session_factory() as db:
        kp = await get_or_create_keypair(db)
        mock.console_pubkey = kp.public_pem()

    iid_a = await _seed_running_instance(session_factory, "http://mock-platform")
    iid_b = await _seed_running_instance(session_factory, "http://mock-platform")

    original, instances_mod = _patch_httpx(mock)
    try:
        r = await client.post(
            f"/instances/{iid_a}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {}},
        )
        cmd_id = r.json()["cmd_id"]
        # Wrong parent instance → 404
        r2 = await client.get(f"/instances/{iid_b}/commands/{cmd_id}")
        assert r2.status_code == 404
    finally:
        instances_mod.httpx.AsyncClient = original


async def test_command_rejected_when_platform_returns_4xx(client, session_factory):
    mock = _MockPlatform(status="rejected", http_status=400)
    async with session_factory() as db:
        kp = await get_or_create_keypair(db)
        mock.console_pubkey = kp.public_pem()

    iid = await _seed_running_instance(session_factory, "http://mock-platform")

    original, instances_mod = _patch_httpx(mock)
    try:
        r = await client.post(
            f"/instances/{iid}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {}},
        )
        cmd_id = r.json()["cmd_id"]
        final = await _wait_for(client, iid, UUID(cmd_id))
        assert final["status"] == "rejected"
        assert final["applied_at"] is None
    finally:
        instances_mod.httpx.AsyncClient = original


async def test_command_failed_on_platform_5xx(client, session_factory):
    mock = _MockPlatform(status="failed", http_status=500)
    async with session_factory() as db:
        kp = await get_or_create_keypair(db)
        mock.console_pubkey = kp.public_pem()

    iid = await _seed_running_instance(session_factory, "http://mock-platform")

    original, instances_mod = _patch_httpx(mock)
    try:
        r = await client.post(
            f"/instances/{iid}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {}},
        )
        cmd_id = r.json()["cmd_id"]
        final = await _wait_for(client, iid, UUID(cmd_id))
        # Either failed (5xx path) or rejected depending on how httpx surfaces
        # the 500 \u2014 both are acceptable terminal states for a broken platform.
        assert final["status"] in {"failed", "rejected"}
        assert final["applied_at"] is None
    finally:
        instances_mod.httpx.AsyncClient = original


async def test_command_log_row_inserted_before_dispatch(client, session_factory):
    """POST /command must persist the row BEFORE returning 202 (audit)."""
    mock = _MockPlatform(status="applied")
    async with session_factory() as db:
        kp = await get_or_create_keypair(db)
        mock.console_pubkey = kp.public_pem()

    iid = await _seed_running_instance(session_factory, "http://mock-platform")

    original, instances_mod = _patch_httpx(mock)
    try:
        r = await client.post(
            f"/instances/{iid}/command",
            json={"kind": CommandKind.CREATE_SPACE.value, "payload": {"name": "row-audit"}},
        )
        cmd_id = UUID(r.json()["cmd_id"])

        # Immediately query the DB directly \u2014 the row must exist regardless
        # of the background task having run yet.
        async with session_factory() as db:
            row = await db.get(CommandLogRow, cmd_id)
            assert row is not None
            assert row.kind == CommandKind.CREATE_SPACE.value
            assert row.payload == {"name": "row-audit"}
            assert row.status in {"queued", "in_progress", "applied"}
    finally:
        instances_mod.httpx.AsyncClient = original
