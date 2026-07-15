"""Local-model registry API — thin CRUD over ``agent_local_model``.

Which browser-local ``.tflite`` models an agent template is *allowed* to fetch
and run via LiteRT.js. Without this whitelist any agent could load an arbitrary
model URL, so registration is the security boundary: every row carries
provenance (``sha256``, ``license``, ``size_bytes``).

Read + register only — models are edited by re-registering. Deletion is
intentionally not exposed here (models are cheap to leave and auditing history
matters more than tidiness at this stage).
"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db import AgentLocalModelRow

router = APIRouter()


class LocalModelOut(BaseModel):
    id: UUID
    template_id: str
    model_url: str
    sha256: str
    size_bytes: int
    license: str
    created_at: datetime
    updated_at: datetime


class LocalModelCreate(BaseModel):
    template_id: str = Field(min_length=1, max_length=128)
    model_url: str = Field(min_length=1)
    sha256: str
    size_bytes: int = Field(ge=0)
    license: str = Field(min_length=1, max_length=64)

    @field_validator("sha256")
    @classmethod
    def _sha_is_hex64(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
            raise ValueError("sha256 must be a 64-char lowercase hex digest")
        return v

    @field_validator("model_url")
    @classmethod
    def _url_scheme(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("model_url must be an http(s) URL with a host")
        return v


def _to_out(row: AgentLocalModelRow) -> LocalModelOut:
    return LocalModelOut(
        id=row.id,
        template_id=row.template_id,
        model_url=row.model_url,
        sha256=row.sha256,
        size_bytes=row.size_bytes,
        license=row.license,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("", response_model=list[LocalModelOut])
async def list_local_models(
    template_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AgentLocalModelRow).order_by(AgentLocalModelRow.created_at.desc())
    if template_id:
        stmt = stmt.where(AgentLocalModelRow.template_id == template_id)
    rows = (await db.execute(stmt)).scalars().all()
    return [_to_out(r) for r in rows]


@router.post("", response_model=LocalModelOut, status_code=status.HTTP_201_CREATED)
async def register_local_model(
    body: LocalModelCreate,
    db: AsyncSession = Depends(get_db),
):
    row = AgentLocalModelRow(
        template_id=body.template_id,
        model_url=body.model_url,
        sha256=body.sha256,
        size_bytes=body.size_bytes,
        license=body.license,
    )
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="this template already registers that model_url",
        )
    await db.refresh(row)
    return _to_out(row)
