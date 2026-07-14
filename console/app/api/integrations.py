"""Integration profiles API — configure, test, and resolve external adapters.

Endpoints:
* ``GET  /integrations/adapters``            — the adapter catalogue (field +
  secret specs; never any secret values).
* ``GET  /integrations/profiles``            — configured profiles (secrets
  redacted to env-name + present flag).
* ``POST /integrations/profiles``            — create a profile.
* ``PATCH /integrations/profiles/{id}``      — update / enable / disable.
* ``DELETE /integrations/profiles/{id}``     — remove a profile.
* ``POST /integrations/profiles/{id}/test``  — run the adapter's health probe.
* ``GET  /integrations/capabilities``        — enabled capabilities for the
  instance (optionally filtered by agent template).
* ``GET  /integrations/resolve``             — profiles serving an agent
  template, for runtime capability resolution (secrets redacted).

Secrets are referenced by environment-variable name and read only at
probe/resolve time. They are never persisted as plaintext nor returned.
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
from app.models.db import IntegrationProfileRow
from app.services.integrations import ADAPTERS, adapter_by_id
from app.services.integrations import probes as probes_mod
from app.services.integrations.resolver import (
    redacted_secret_refs,
    resolve_capabilities,
    resolve_secret_values,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AdapterOut(BaseModel):
    id: str
    name: str
    category: str
    provider: str
    capabilities: list[str]
    probe: str
    integration: str
    base_url_default: str | None
    fields: list[dict]
    secrets: list[dict]
    docs_url: str | None
    template_id: str | None
    tags: list[str]
    notes: str | None


class ProfileOut(BaseModel):
    id: UUID
    adapter_id: str
    name: str
    base_url: str | None
    config: dict
    secret_refs: list[dict]
    template_ids: list[str]
    enabled: bool
    capabilities: list[str]
    created_at: datetime
    updated_at: datetime


def _validate_base_url(v: str | None) -> str | None:
    if v is None or v == "":
        return None
    parsed = urlparse(v)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base_url must be an http(s) URL with a host")
    return v


def _validate_secret_refs(v: dict) -> dict:
    # Guard against anyone stuffing a value here: env var names are short
    # tokens without spaces, never long secrets.
    for k, name in v.items():
        if not isinstance(name, str) or len(name) > 128 or " " in name:
            raise ValueError(f"secret_refs[{k}] must be an environment variable name")
    return v


class ProfileCreate(BaseModel):
    adapter_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    base_url: str | None = None
    config: dict = Field(default_factory=dict)
    secret_refs: dict = Field(default_factory=dict)
    template_ids: list[str] = Field(default_factory=list)
    enabled: bool = False

    @field_validator("base_url")
    @classmethod
    def _url_ok(cls, v: str | None) -> str | None:
        return _validate_base_url(v)

    @field_validator("secret_refs")
    @classmethod
    def _refs_ok(cls, v: dict) -> dict:
        return _validate_secret_refs(v)


class ProfilePatch(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    base_url: str | None = None
    config: dict | None = None
    secret_refs: dict | None = None
    template_ids: list[str] | None = None
    enabled: bool | None = None

    @field_validator("base_url")
    @classmethod
    def _url_ok(cls, v: str | None) -> str | None:
        return _validate_base_url(v)

    @field_validator("secret_refs")
    @classmethod
    def _refs_ok(cls, v: dict | None) -> dict | None:
        return _validate_secret_refs(v) if v is not None else v


class ProbeOut(BaseModel):
    state: str
    detail: str | None = None
    latency_ms: float | None = None
    checked_url: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _adapter_out(ad) -> AdapterOut:
    return AdapterOut(
        id=ad.id, name=ad.name, category=ad.category, provider=ad.provider,
        capabilities=ad.capabilities, probe=ad.probe.value, integration=ad.integration,
        base_url_default=ad.base_url_default,
        fields=[f.model_dump() for f in ad.fields],
        secrets=[{"key": s.key, "label": s.label, "env": s.env, "required": s.required} for s in ad.secrets],
        docs_url=ad.docs_url, template_id=ad.template_id, tags=ad.tags, notes=ad.notes,
    )


def _profile_out(row: IntegrationProfileRow) -> ProfileOut:
    adapter = adapter_by_id(row.adapter_id)
    return ProfileOut(
        id=row.id,
        adapter_id=row.adapter_id,
        name=row.name,
        base_url=row.base_url,
        config=row.config_json or {},
        secret_refs=redacted_secret_refs(adapter, row) if adapter else [],
        template_ids=row.template_ids_json or [],
        enabled=row.enabled,
        capabilities=adapter.capabilities if adapter else [],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _get_row(profile_id: UUID, db: AsyncSession) -> IntegrationProfileRow:
    row = await db.get(IntegrationProfileRow, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="integration profile not found")
    return row


# ---------------------------------------------------------------------------
# Adapters catalogue
# ---------------------------------------------------------------------------

@router.get("/adapters", response_model=list[AdapterOut])
async def list_adapters(category: str | None = None):
    ads = ADAPTERS if category is None else [a for a in ADAPTERS if a.category == category]
    return [_adapter_out(a) for a in ads]


# ---------------------------------------------------------------------------
# Profiles CRUD
# ---------------------------------------------------------------------------

@router.get("/profiles", response_model=list[ProfileOut])
async def list_profiles(adapter_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(IntegrationProfileRow).order_by(IntegrationProfileRow.created_at.desc())
    if adapter_id:
        stmt = stmt.where(IntegrationProfileRow.adapter_id == adapter_id)
    rows = (await db.execute(stmt)).scalars().all()
    return [_profile_out(r) for r in rows]


@router.post("/profiles", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def create_profile(body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    if adapter_by_id(body.adapter_id) is None:
        raise HTTPException(status_code=422, detail=f"unknown adapter_id: {body.adapter_id}")
    row = IntegrationProfileRow(
        adapter_id=body.adapter_id,
        name=body.name,
        base_url=body.base_url,
        config_json=body.config,
        secret_refs_json=body.secret_refs,
        template_ids_json=body.template_ids,
        enabled=body.enabled,
    )
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="a profile with that adapter_id + name already exists")
    await db.refresh(row)
    return _profile_out(row)


@router.patch("/profiles/{profile_id}", response_model=ProfileOut)
async def update_profile(profile_id: UUID, body: ProfilePatch, db: AsyncSession = Depends(get_db)):
    row = await _get_row(profile_id, db)
    data = body.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        row.name = data["name"]
    if "base_url" in data:
        row.base_url = data["base_url"]
    if "config" in data and data["config"] is not None:
        row.config_json = data["config"]
    if "secret_refs" in data and data["secret_refs"] is not None:
        row.secret_refs_json = data["secret_refs"]
    if "template_ids" in data and data["template_ids"] is not None:
        row.template_ids_json = data["template_ids"]
    if "enabled" in data and data["enabled"] is not None:
        row.enabled = data["enabled"]
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="a profile with that adapter_id + name already exists")
    await db.refresh(row)
    return _profile_out(row)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await _get_row(profile_id, db)
    await db.delete(row)
    await db.commit()


# ---------------------------------------------------------------------------
# Connection test
# ---------------------------------------------------------------------------

@router.post("/profiles/{profile_id}/test", response_model=ProbeOut)
async def test_profile(profile_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await _get_row(profile_id, db)
    adapter = adapter_by_id(row.adapter_id)
    if adapter is None:
        raise HTTPException(status_code=422, detail=f"unknown adapter_id: {row.adapter_id}")
    secrets = resolve_secret_values(adapter, row)
    result = await probes_mod.probe(
        adapter,
        base_url=row.base_url,
        secrets=secrets,
        config=row.config_json or {},
    )
    return ProbeOut(**result.model_dump())


# ---------------------------------------------------------------------------
# Runtime capability resolution
# ---------------------------------------------------------------------------

@router.get("/capabilities")
async def list_capabilities(template_id: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(IntegrationProfileRow))).scalars().all()
    caps = resolve_capabilities(list(rows), template_id=template_id, enabled_only=True)
    return {"template_id": template_id, "capabilities": caps}


@router.get("/resolve")
async def resolve_for_template(template_id: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(IntegrationProfileRow))).scalars().all()
    caps = resolve_capabilities(list(rows), template_id=template_id, enabled_only=True)
    by_capability: dict[str, list[dict]] = {}
    for c in caps:
        by_capability.setdefault(c["capability"], []).append(c)
    return {"template_id": template_id, "by_capability": by_capability, "capabilities": caps}
