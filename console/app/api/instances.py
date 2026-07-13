"""Instances endpoints — CRUD stub for the Instance Registry."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


# ---------- Schemas (stub — will move to nexus-core) ----------

class InstanceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    persona_display_name: str
    modality: str = Field(..., description="local | fly | k8s | onprem | saas")
    llm_providers: list[str] = Field(default_factory=list)
    areas: list[str] = Field(default_factory=list)


class InstanceOut(BaseModel):
    instance_id: UUID
    name: str
    persona_display_name: str
    modality: str
    endpoint: str | None
    version: str | None
    status: str
    created_at: datetime


# ---------- In-memory stub registry (TODO: replace with Postgres) ----------

_REGISTRY: dict[UUID, InstanceOut] = {}


@router.get("", response_model=list[InstanceOut])
async def list_instances():
    return list(_REGISTRY.values())


@router.post("", response_model=InstanceOut, status_code=status.HTTP_201_CREATED)
async def create_instance(body: InstanceCreate):
    iid = uuid4()
    instance = InstanceOut(
        instance_id=iid,
        name=body.name,
        persona_display_name=body.persona_display_name,
        modality=body.modality,
        endpoint=None,
        version=None,
        status="bootstrap-pending",
        created_at=datetime.now(timezone.utc),
    )
    _REGISTRY[iid] = instance
    # TODO: dispatch wizard + deployer
    return instance


@router.get("/{instance_id}", response_model=InstanceOut)
async def get_instance(instance_id: UUID):
    if instance_id not in _REGISTRY:
        raise HTTPException(status_code=404, detail="instance not found")
    return _REGISTRY[instance_id]


@router.post("/{instance_id}/command", status_code=status.HTTP_202_ACCEPTED)
async def send_command(instance_id: UUID, payload: dict):
    if instance_id not in _REGISTRY:
        raise HTTPException(status_code=404, detail="instance not found")
    # TODO: sign JWT with console key, POST to platform /_console/command
    return {"accepted": True, "command": payload.get("cmd"), "instance_id": str(instance_id)}
