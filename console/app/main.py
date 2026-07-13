"""Nexus Console FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import instances, platform_notify, providers, health, wizard
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: TODO — check DB, load console keys, warm registry cache
    yield
    # Shutdown: TODO — close connections


app = FastAPI(
    title="Nexus Console",
    description="Control plane for Nexus OS — deploys and manages Platform instances.",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["health"])
app.include_router(instances.router, prefix="/instances", tags=["instances"])
app.include_router(providers.router, prefix="/providers", tags=["providers"])
app.include_router(wizard.router, prefix="/wizard", tags=["wizard"])
app.include_router(platform_notify.router, prefix="/_platform", tags=["platform-callbacks"])


@app.get("/", tags=["root"])
async def root():
    return {
        "product": "Nexus Console",
        "version": __version__,
        "docs": "/docs",
    }
