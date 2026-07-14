"""Connection probes for integration adapters.

One async ``probe(...)`` entry point dispatches on :class:`ProbeKind`. Every
probe is best-effort and never raises: it returns a typed :class:`ProbeResult`
so the UI can render an honest state instead of an error toast.

Secrets arrive already resolved (logical key -> value) from
:mod:`app.services.integrations.resolver`; this module never reads the
environment or the database itself, which keeps it trivially unit-testable by
monkeypatching :data:`httpx`.
"""

from __future__ import annotations

import time
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from app.services.integrations.registry import Adapter, ProbeKind

_TIMEOUT_S = 5.0

# Probe outcome states.
REACHABLE = "reachable"
UNREACHABLE = "unreachable"
UNCONFIGURED = "unconfigured"
INVALID_URL = "invalid_url"
SECRET_MISSING = "secret_missing"
NO_PROBE = "no_probe"


class ProbeResult(BaseModel):
    state: str
    detail: str | None = None
    latency_ms: float | None = None
    checked_url: str | None = None


def _valid_url(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _missing_required_secret(adapter: Adapter, secrets: dict[str, str]) -> str | None:
    for spec in adapter.secrets:
        if spec.required and not secrets.get(spec.key):
            return spec.env
    return None


def _join(base: str, path: str) -> str:
    return base.rstrip("/") + (path if path.startswith("/") else f"/{path}")


async def _http_get(url: str, headers: dict[str, str], *, auth=None) -> ProbeResult:
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_S, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers, auth=auth)
    except httpx.HTTPError as exc:
        return ProbeResult(state=UNREACHABLE, detail=f"{type(exc).__name__}: {exc}"[:300], checked_url=url)
    latency = round((time.perf_counter() - t0) * 1000.0, 1)
    if resp.status_code >= 400:
        return ProbeResult(
            state=UNREACHABLE,
            detail=f"HTTP {resp.status_code}",
            latency_ms=latency,
            checked_url=url,
        )
    return ProbeResult(state=REACHABLE, latency_ms=latency, checked_url=url)


async def probe(
    adapter: Adapter,
    *,
    base_url: str | None,
    secrets: dict[str, str],
    config: dict[str, str] | None = None,
) -> ProbeResult:
    """Run the adapter's connection probe. Never raises."""
    config = config or {}
    kind = adapter.probe

    if kind == ProbeKind.no_probe:
        return ProbeResult(state=NO_PROBE, detail=adapter.notes or "No automated probe for this adapter.")

    if kind == ProbeKind.key_present:
        missing = _missing_required_secret(adapter, secrets)
        if missing:
            return ProbeResult(state=SECRET_MISSING, detail=f"env {missing} is not set")
        return ProbeResult(state=REACHABLE, detail="credentials present (no live probe performed)")

    if kind == ProbeKind.postgres:
        return await _probe_postgres(adapter, secrets)

    # From here every probe is an HTTP GET against a base URL.
    url_base = base_url or adapter.base_url_default
    if not _valid_url(url_base):
        if not url_base:
            return ProbeResult(state=UNCONFIGURED, detail="No base URL configured.")
        return ProbeResult(state=INVALID_URL, detail="base_url must be http(s) with a host.")

    missing = _missing_required_secret(adapter, secrets)
    if missing:
        return ProbeResult(state=SECRET_MISSING, detail=f"env {missing} is not set")

    headers: dict[str, str] = {}
    auth = None
    url = _join(url_base, adapter.probe_path)

    if kind == ProbeKind.openai_compat:
        key = secrets.get("api_key")
        if key:
            headers["Authorization"] = f"Bearer {key}"
    elif kind == ProbeKind.header_key:
        key = secrets.get("api_key")
        if key and adapter.auth_header:
            headers[adapter.auth_header] = f"{adapter.auth_scheme} {key}" if adapter.auth_scheme else key
        extra = config.get("anthropic_version")
        if extra:
            headers["anthropic-version"] = extra
    elif kind == ProbeKind.query_key:
        key = secrets.get("api_key")
        if key and adapter.query_param:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{adapter.query_param}={key}"
    elif kind == ProbeKind.basic_auth:
        user = secrets.get("username")
        pwd = secrets.get("password")
        if user is not None:
            auth = (user, pwd or "")
    elif kind == ProbeKind.http_health:
        key = secrets.get("api_key")
        if key:
            headers["Authorization"] = f"Bearer {key}"

    return await _http_get(url, headers, auth=auth)


async def _probe_postgres(adapter: Adapter, secrets: dict[str, str]) -> ProbeResult:
    dsn = secrets.get("dsn")
    if not dsn:
        return ProbeResult(state=SECRET_MISSING, detail="env PGVECTOR_DSN is not set")

    # Normalise to an async driver so we can SELECT 1 without a sync engine.
    async_dsn = dsn
    if async_dsn.startswith("postgresql://"):
        async_dsn = async_dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif async_dsn.startswith("postgres://"):
        async_dsn = async_dsn.replace("postgres://", "postgresql+asyncpg://", 1)

    t0 = time.perf_counter()
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(async_dsn, pool_pre_ping=False)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        finally:
            await engine.dispose()
    except Exception as exc:  # noqa: BLE001 — any connect error => unreachable
        return ProbeResult(state=UNREACHABLE, detail=f"{type(exc).__name__}: {exc}"[:300])
    latency = round((time.perf_counter() - t0) * 1000.0, 1)
    return ProbeResult(state=REACHABLE, latency_ms=latency)
