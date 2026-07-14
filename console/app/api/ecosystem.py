"""Ecosystem / capability registry — read-only discovery API.

Surfaces the honest AI-ecosystem catalogue (LLMs, frameworks, vector DBs,
extraction, embeddings, evaluation) plus the two local-first capabilities this
repo actually ships (LiteRT.js and the optional Voicebox sidecar). See
``app.services.ecosystem`` for the status/integration model.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import __version__
from app.core.config import settings
from app.services.ecosystem import EcosystemEntry, EcosystemView, build_registry, build_view

router = APIRouter()


@router.get("", response_model=EcosystemView)
async def get_ecosystem() -> EcosystemView:
    """Full ecosystem grouped by category with per-status counts."""
    return build_view(settings, __version__)


@router.get("/{entry_id}", response_model=EcosystemEntry)
async def get_ecosystem_entry(entry_id: str) -> EcosystemEntry:
    match = next((e for e in build_registry(settings) if e.id == entry_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"ecosystem entry {entry_id!r} not found")
    return match
