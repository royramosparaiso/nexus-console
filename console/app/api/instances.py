"""Instances endpoints — persistent registry backed by SQLAlchemy."""

from __future__ import annotations

import time
from datetime import datetime
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_core.contracts.commands import (
    Command, CommandEnvelope, CommandKind,
)
from nexus_core.jwt import sign_command

from app.db import get_db
from app.models.db import InstanceRow
from app.services.keypair import get_or_create_keypair

router = APIRouter()


class InstanceOut(BaseModel):
    instance_id: UUID
    name: str
    persona_display_name: str
    persona_kind: str
    modality: str
    agent_runtime: str
    auth_provider: str
    endpoint: str | None
    version: str | None
    status: str
    error_detail: str | None = None
    created_at: datetime
    bootstrapped_at: datetime | None = None


def _to_out(row: InstanceRow) -> InstanceOut:
    return InstanceOut(
        instance_id=row.id,
        name=row.name,
        persona_display_name=row.persona_display_name,
        persona_kind=row.persona_kind,
        modality=row.modality,
        agent_runtime=row.agent_runtime,
        auth_provider=row.auth_provider,
        endpoint=row.endpoint,
        version=row.platform_version,
        status=row.status,
        error_detail=row.error_detail,
        created_at=row.created_at,
        bootstrapped_at=row.bootstrapped_at,
    )


@router.get("", response_model=list[InstanceOut])
async def list_instances(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(InstanceRow).order_by(InstanceRow.created_at.desc()))).scalars().all()
    return [_to_out(r) for r in rows]


@router.get("/{instance_id}", response_model=InstanceOut)
async def get_instance(instance_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(InstanceRow, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail="instance not found")
    return _to_out(row)


class CommandRequest(BaseModel):
    kind: CommandKind
    payload: dict = {}


class CommandResponse(BaseModel):
    accepted: bool
    cmd_id: UUID
    status: str
    detail: str | None = None


@router.post("/{instance_id}/command", response_model=CommandResponse)
async def send_command(
    instance_id: UUID, body: CommandRequest, db: AsyncSession = Depends(get_db),
):
    """Sign a JWT command and POST it to the Platform's /_commands."""
    row = await db.get(InstanceRow, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail="instance not found")
    if row.status != "running" or not row.endpoint:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"instance not running (status={row.status})",
        )
    kp = await get_or_create_keypair(db)

    now = int(time.time())
    env = CommandEnvelope(
        instance_id=row.id,
        issued_at=now,
        expires_at=now + 300,
        command=Command(kind=body.kind, payload=body.payload),
    )
    token = sign_command(kp, env)

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{row.endpoint}/_commands",
            content=token,
            headers={"Content-Type": "application/jwt"},
        )
    if r.status_code >= 500:
        raise HTTPException(status_code=502, detail=f"platform error: {r.text[:200]}")
    result = r.json()
    return CommandResponse(
        accepted=r.status_code < 400,
        cmd_id=env.cmd_id,
        status=result.get("status", "unknown"),
        detail=result.get("detail"),
    )
