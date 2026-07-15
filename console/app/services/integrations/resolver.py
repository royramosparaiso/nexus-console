"""Resolve integration profiles into secrets, redacted views, and capabilities.

This module is the single place that touches ``os.environ`` for integration
secrets. It reads values *only* to pass them to a probe or to a runtime
capability resolution; it never returns raw secret values to the API layer.
"""

from __future__ import annotations

import os

from app.models.db import IntegrationProfileRow
from app.services.integrations.registry import Adapter, adapter_by_id


def effective_env(adapter: Adapter, profile: IntegrationProfileRow, key: str) -> str | None:
    """The env var name a profile reads a logical secret from (ref overrides default)."""
    override = (profile.secret_refs_json or {}).get(key)
    if override:
        return override
    for spec in adapter.secrets:
        if spec.key == key:
            return spec.env
    return None


def resolve_secret_values(adapter: Adapter, profile: IntegrationProfileRow) -> dict[str, str]:
    """Read the actual secret values from the environment. Never persisted."""
    values: dict[str, str] = {}
    for spec in adapter.secrets:
        env = effective_env(adapter, profile, spec.key)
        if env:
            val = os.environ.get(env)
            if val:
                values[spec.key] = val
    return values


def redacted_secret_refs(adapter: Adapter, profile: IntegrationProfileRow) -> list[dict]:
    """Return per-secret {key, env, present} — the env NAME and whether it's set.

    The value itself is never included.
    """
    out: list[dict] = []
    for spec in adapter.secrets:
        env = effective_env(adapter, profile, spec.key)
        out.append(
            {
                "key": spec.key,
                "label": spec.label,
                "env": env,
                "required": spec.required,
                "present": bool(env and os.environ.get(env)),
            }
        )
    return out


def profile_serves_template(profile: IntegrationProfileRow, template_id: str | None) -> bool:
    """A profile serves an agent template if it is global or lists that template."""
    refs = profile.template_ids_json or []
    if not refs:
        return True
    if template_id is None:
        return False
    return template_id in refs


def resolve_capabilities(
    profiles: list[IntegrationProfileRow],
    *,
    template_id: str | None = None,
    enabled_only: bool = True,
) -> list[dict]:
    """Flatten enabled profiles into capability entries for agent/sidecar manifests.

    Secrets are redacted to presence flags only.
    """
    out: list[dict] = []
    for p in profiles:
        if enabled_only and not p.enabled:
            continue
        adapter = adapter_by_id(p.adapter_id)
        if adapter is None:
            continue
        if template_id is not None and not profile_serves_template(p, template_id):
            continue
        for cap in adapter.capabilities:
            out.append(
                {
                    "capability": cap,
                    "adapter_id": adapter.id,
                    "provider": adapter.provider,
                    "category": adapter.category,
                    "profile_id": str(p.id),
                    "profile_name": p.name,
                    "base_url": p.base_url or adapter.base_url_default,
                    "integration": adapter.integration,
                    "secrets_present": all(
                        r["present"] for r in redacted_secret_refs(adapter, p) if r["required"]
                    ),
                }
            )
    return out
