"""Voicebox integration — optional local-first voice sidecar.

Voicebox (https://github.com/jamiepine/voicebox) is an open-source, local TTS/
STT app exposing a REST API and an HTTP MCP server. It runs *outside* Nexus as
a separate local or self-hosted process. Nexus never bundles it and never sends
audio anywhere on its own — it only talks to a base URL the operator configures
and reports reachability.

This module is deliberately a thin, safe client:
* Config is read from ``Settings`` (env), so the API key lives server-side and
  is never returned to the browser (only ``api_key_configured: bool``).
* The base URL is validated (http/https, host present) before any request.
* Health checks are best-effort with a short timeout and never raise; a
  disabled or unconfigured integration returns a clear, typed state instead of
  an error.
* Voice cloning is opt-in. The consent flag is surfaced but Nexus performs no
  cloning and uploads no audio from here — that action lives in Voicebox.
"""

from __future__ import annotations

import time
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

_HEALTH_TIMEOUT_S = 4.0


class VoiceboxConfig(BaseModel):
    enabled: bool
    base_url: str | None
    mcp_url: str | None
    # Redacted — we only ever say whether a key exists, never its value.
    api_key_configured: bool
    voice_cloning_consent: bool
    # True when enabled + a syntactically valid base URL is present.
    configured: bool


class VoiceboxStatus(BaseModel):
    # One of: disabled | unconfigured | invalid_url | reachable | unreachable
    state: str
    detail: str | None = None
    base_url: str | None = None
    latency_ms: float | None = None
    version: str | None = None


class CloningConsentOut(BaseModel):
    # Whether Nexus is permitted to expose Voicebox voice-cloning affordances.
    consent: bool
    # Human-readable ownership/consent statement shown in the UI.
    notice: str


_CLONING_NOTICE = (
    "Voice cloning is opt-in. Only clone a voice you own or have explicit, "
    "documented permission to use. Nexus never uploads audio on your behalf — "
    "cloning happens entirely inside your local Voicebox instance from a "
    "reference clip you provide there."
)


def _valid_base_url(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _mcp_url() -> str | None:
    if not _valid_base_url(settings.voicebox_base_url):
        return None
    base = settings.voicebox_base_url.rstrip("/")
    path = settings.voicebox_mcp_path if settings.voicebox_mcp_path.startswith("/") else f"/{settings.voicebox_mcp_path}"
    return f"{base}{path}"


def _config() -> VoiceboxConfig:
    valid = _valid_base_url(settings.voicebox_base_url)
    return VoiceboxConfig(
        enabled=settings.voicebox_enabled,
        base_url=settings.voicebox_base_url,
        mcp_url=_mcp_url(),
        api_key_configured=bool(settings.voicebox_api_key),
        voice_cloning_consent=settings.voicebox_voice_cloning_consent,
        configured=settings.voicebox_enabled and valid,
    )


@router.get("/config", response_model=VoiceboxConfig)
async def get_config() -> VoiceboxConfig:
    return _config()


@router.get("/cloning-consent", response_model=CloningConsentOut)
async def get_cloning_consent() -> CloningConsentOut:
    return CloningConsentOut(
        consent=settings.voicebox_voice_cloning_consent,
        notice=_CLONING_NOTICE,
    )


@router.get("/status", response_model=VoiceboxStatus)
async def get_status() -> VoiceboxStatus:
    """Best-effort reachability probe against the configured Voicebox base URL.

    Never raises: returns a typed ``state`` so the UI can render an honest
    disabled/unconfigured/unreachable panel instead of an error toast.
    """
    if not settings.voicebox_enabled:
        return VoiceboxStatus(state="disabled", detail="Voicebox integration is turned off.")

    base = settings.voicebox_base_url
    if not _valid_base_url(base):
        if not base:
            return VoiceboxStatus(state="unconfigured", detail="No base URL set (CONSOLE_VOICEBOX_BASE_URL).")
        return VoiceboxStatus(state="invalid_url", detail="Base URL must be http(s) with a host.", base_url=base)

    headers = {}
    if settings.voicebox_api_key:
        headers["Authorization"] = f"Bearer {settings.voicebox_api_key}"

    url = base.rstrip("/") + "/health"
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=_HEALTH_TIMEOUT_S) as client:
            resp = await client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        return VoiceboxStatus(
            state="unreachable",
            detail=f"{type(exc).__name__}: {exc}"[:300],
            base_url=base,
        )

    latency = (time.perf_counter() - t0) * 1000.0
    if resp.status_code >= 400:
        return VoiceboxStatus(
            state="unreachable",
            detail=f"health returned HTTP {resp.status_code}",
            base_url=base,
            latency_ms=round(latency, 1),
        )

    version = None
    try:
        body = resp.json()
        if isinstance(body, dict):
            version = body.get("version") or body.get("voicebox_version")
    except Exception:  # noqa: BLE001 — non-JSON health body is fine
        pass

    return VoiceboxStatus(
        state="reachable",
        base_url=base,
        latency_ms=round(latency, 1),
        version=version,
    )
