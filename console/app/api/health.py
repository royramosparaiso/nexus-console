"""Health + readiness."""

from fastapi import APIRouter

from app import __version__

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "version": __version__}


@router.get("/ready")
async def ready():
    # TODO: check DB, Redis, keys
    return {"status": "ready"}
