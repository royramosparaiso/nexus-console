"""Instances endpoints — persistent registry backed by SQLAlchemy.

Commands are dispatched asynchronously (from the client's point of view):
the POST /command endpoint records a command_log row in `queued` state,
schedules a background task that signs + POSTs to the Platform, and returns
the cmd_id immediately. The client then polls GET /commands/{cmd_id} to
observe the queued → in_progress → applied|failed|rejected transitions.

The Platform itself still responds synchronously today — but the Console's
async layer gives us an audit log, a progress-visible UI, and a hook to
support long-running commands (e.g. image pulls) without changing the API
contract later.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_core.contracts.commands import (
    Command, CommandEnvelope, CommandKind,
)
from nexus_core.jwt import sign_command

from app import db as db_module
from app.db import get_db
from app.models.db import CommandLogRow, InstanceRow
from app.services.keypair import get_or_create_keypair

router = APIRouter()

logger = logging.getLogger(__name__)


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
    local_inference: bool = False
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
        local_inference=row.local_inference,
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


class InstancePatch(BaseModel):
    """Partial update for an instance. Only feature flags are mutable here.

    All fields optional so old clients that omit them keep prior behaviour.
    """

    local_inference: bool | None = None


@router.patch("/{instance_id}", response_model=InstanceOut)
async def update_instance(
    instance_id: UUID,
    body: InstancePatch,
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(InstanceRow, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail="instance not found")
    if body.local_inference is not None:
        row.local_inference = body.local_inference
    await db.commit()
    await db.refresh(row)
    return _to_out(row)


class CommandRequest(BaseModel):
    kind: CommandKind
    payload: dict = {}


class CommandAccepted(BaseModel):
    """Response to POST /command — the command is queued, not yet applied.

    The client is expected to poll GET /commands/{cmd_id} for status.
    """

    accepted: bool
    cmd_id: UUID
    status: str  # always "queued" on success
    detail: str | None = None


class CommandStatusOut(BaseModel):
    cmd_id: UUID
    instance_id: UUID
    kind: str
    status: str
    detail: str | None = None
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime
    applied_at: datetime | None = None


def _to_status(row: CommandLogRow) -> CommandStatusOut:
    return CommandStatusOut(
        cmd_id=row.cmd_id,
        instance_id=row.instance_id,
        kind=row.kind,
        status=row.status,
        detail=row.detail,
        error_code=row.error_code,
        created_at=row.created_at,
        updated_at=row.updated_at,
        applied_at=row.applied_at,
    )


@router.post(
    "/{instance_id}/command",
    response_model=CommandAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_command(
    instance_id: UUID,
    body: CommandRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Queue a signed command for the given instance.

    Returns 202 with cmd_id + status=queued immediately. The actual
    JWT signing + platform POST runs in a background task; the client
    polls GET /commands/{cmd_id} to see progress.
    """
    row = await db.get(InstanceRow, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail="instance not found")
    if row.status != "running" or not row.endpoint:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"instance not running (status={row.status})",
        )

    cmd_id = uuid4()
    log = CommandLogRow(
        cmd_id=cmd_id,
        instance_id=instance_id,
        kind=body.kind.value if hasattr(body.kind, "value") else str(body.kind),
        payload=body.payload,
        status="queued",
    )
    db.add(log)
    await db.commit()

    background_tasks.add_task(
        _dispatch_command,
        cmd_id=cmd_id,
        instance_id=instance_id,
        kind=body.kind,
        payload=body.payload,
    )

    return CommandAccepted(
        accepted=True,
        cmd_id=cmd_id,
        status="queued",
        detail=None,
    )


@router.get(
    "/{instance_id}/commands/{cmd_id}",
    response_model=CommandStatusOut,
)
async def get_command_status(
    instance_id: UUID,
    cmd_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(CommandLogRow, cmd_id)
    if row is None or row.instance_id != instance_id:
        raise HTTPException(status_code=404, detail="command not found")
    return _to_status(row)


async def _dispatch_command(
    cmd_id: UUID,
    instance_id: UUID,
    kind: CommandKind,
    payload: dict,
) -> None:
    """Background task: sign the envelope and POST to the Platform.

    Opens its own DB session (BackgroundTasks runs after the request's
    session is closed).
    """
    try:
        await _dispatch_command_inner(cmd_id, instance_id, kind, payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("command dispatch crashed: cmd_id=%s", cmd_id)
        # Best-effort: mark the row as failed so the client stops polling.
        try:
            session_factory = db_module.SessionLocal
            async with session_factory() as session:
                log = await session.get(CommandLogRow, cmd_id)
                if log is not None:
                    from datetime import timezone
                    log.status = "failed"
                    log.error_code = "internal_error"
                    log.detail = f"{type(exc).__name__}: {exc}"[:500]
                    log.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    await session.commit()
        except Exception:
            logger.exception("could not mark command as failed")


async def _dispatch_command_inner(
    cmd_id: UUID,
    instance_id: UUID,
    kind: CommandKind,
    payload: dict,
) -> None:
    from datetime import timezone
    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    # Use the current SessionLocal (tests override it by monkey-patching
    # app.db.SessionLocal via the dependency override on get_db).
    session_factory = db_module.SessionLocal
    async with session_factory() as session:
        # Transition queued → in_progress
        log = await session.get(CommandLogRow, cmd_id)
        if log is None:
            logger.warning("command log missing for cmd_id=%s", cmd_id)
            return
        log.status = "in_progress"
        log.updated_at = now_dt
        await session.commit()

        row = await session.get(InstanceRow, instance_id)
        if row is None or row.status != "running" or not row.endpoint:
            log.status = "rejected"
            log.error_code = "instance_unavailable"
            log.detail = f"instance status={row.status if row else 'missing'}"
            log.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await session.commit()
            return

        kp = await get_or_create_keypair(session)

        now = int(time.time())
        env = CommandEnvelope(
            cmd_id=cmd_id,
            instance_id=row.id,
            issued_at=now,
            expires_at=now + 300,
            command=Command(kind=kind, payload=payload),
        )
        token = sign_command(kp, env)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    f"{row.endpoint}/_commands",
                    content=token,
                    headers={"Content-Type": "application/jwt"},
                )
        except (httpx.HTTPError, asyncio.TimeoutError) as exc:
            log = await session.get(CommandLogRow, cmd_id)
            log.status = "failed"
            log.error_code = "network_error"
            log.detail = str(exc)[:500]
            log.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await session.commit()
            return

        try:
            result = r.json()
        except Exception:
            result = {}

        log = await session.get(CommandLogRow, cmd_id)
        if r.status_code >= 500:
            log.status = "failed"
            log.error_code = "platform_error"
            log.detail = r.text[:500]
        elif r.status_code >= 400:
            log.status = "rejected"
            log.error_code = result.get("error_code", "http_error")
            log.detail = result.get("detail") or r.text[:500]
        else:
            log.status = result.get("status", "applied")
            log.detail = result.get("detail")
            log.error_code = result.get("error_code")
            if log.status == "applied":
                log.applied_at = datetime.now(timezone.utc).replace(tzinfo=None)
        log.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.commit()
