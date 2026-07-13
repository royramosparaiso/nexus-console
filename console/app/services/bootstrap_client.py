"""Console → Platform bootstrap client.

Waits for Platform's /_health, then POST /_bootstrap with the manifest and the
one-time token. On success, updates the InstanceRow.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_core.contracts.bootstrap import (
    BootstrapRequest, BootstrapResponse, BootstrapStatus,
)
from nexus_core.jwt import ConsoleKeypair
from nexus_core.models import InstanceManifest

from app.models.db import InstanceRow


class BootstrapError(RuntimeError):
    pass


async def wait_healthy(endpoint: str, timeout_s: float = 60.0) -> None:
    """Poll /_health until 200 or timeout."""
    deadline = asyncio.get_event_loop().time() + timeout_s
    async with httpx.AsyncClient(timeout=2.0) as client:
        while asyncio.get_event_loop().time() < deadline:
            try:
                r = await client.get(f"{endpoint}/_health")
                if r.status_code == 200:
                    return
            except (httpx.ConnectError, httpx.ReadError, httpx.TimeoutException):
                pass
            await asyncio.sleep(1.0)
    raise BootstrapError(f"platform at {endpoint} did not become healthy in {timeout_s}s")


async def dispatch_bootstrap(
    db: AsyncSession,
    row: InstanceRow,
    endpoint: str,
    token: str,
    console_kp: ConsoleKeypair,
    manifest: InstanceManifest,
    webhook_url: str,
    http_client: httpx.AsyncClient | None = None,
) -> BootstrapResponse:
    """Perform the /_bootstrap handshake and update the DB row."""
    req = BootstrapRequest(
        instance_id=row.id,
        console_public_key_pem=console_kp.public_pem(),
        console_webhook_url=webhook_url,
        manifest=manifest,
    )
    close_after = False
    client = http_client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
        close_after = True
    try:
        r = await client.post(
            f"{endpoint}/_bootstrap",
            json=req.model_dump(mode="json"),
            headers={"X-Bootstrap-Token": token},
        )
    finally:
        if close_after:
            await client.aclose()
    if r.status_code != 200:
        raise BootstrapError(f"platform returned {r.status_code}: {r.text[:500]}")
    resp = BootstrapResponse.model_validate(r.json())

    if resp.status in (BootstrapStatus.OK, BootstrapStatus.ALREADY_BOOTSTRAPPED):
        row.platform_public_key_pem = resp.platform_public_key_pem
        row.platform_version = resp.platform_version
        row.endpoint = endpoint
        row.status = "running"
        row.bootstrap_token = None  # burn it
        from datetime import datetime, timezone
        row.bootstrapped_at = datetime.now(timezone.utc)
    else:
        row.status = "bootstrap-failed"
        row.error_detail = resp.error_detail or resp.status.value
    await db.commit()
    return resp
