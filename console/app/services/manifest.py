"""Convert wizard submission → nexus_core.InstanceManifest.

The wizard's Pydantic schemas historically diverged slightly from `nexus_core`
models (Clerk, AgentRuntime, AuthConfig were added later). This adapter
builds a well-formed InstanceManifest from either legacy or fresh submissions.
"""

from __future__ import annotations

from typing import Any

from nexus_core.models import (
    AreasConfig, AuthConfig, DeploymentConfig, GovernanceConfig,
    InstanceManifest, LlmConfig, LlmRoleAssignment, MemoryConfig, PersonaConfig,
)

from app.models.wizard import WizardSubmission


def submission_to_manifest(sub: WizardSubmission) -> InstanceManifest:
    """Build the canonical shared InstanceManifest from the wizard payload."""

    # Auth config — v0.6 additions (Clerk etc.) — accept from sub if present
    # via an extra `governance.auth` payload, otherwise default.
    auth_extra: dict[str, Any] = getattr(sub.governance, "auth", None) or {}
    auth = AuthConfig(**auth_extra) if auth_extra else AuthConfig()

    # Runtime — same idea
    runtime = getattr(sub.deployment, "runtime", None) or "in_process"
    worker_replicas = getattr(sub.deployment, "worker_replicas", None) or 1

    return InstanceManifest(
        name=sub.instance_name,
        persona=PersonaConfig(
            display_name=sub.persona.display_name,
            kind=sub.persona.kind,
            description=sub.persona.description,
            default_locale=sub.persona.default_locale,
        ),
        deployment=DeploymentConfig(
            modality=sub.deployment.modality,
            domain=sub.deployment.domain,
            region=sub.deployment.region,
            tls=sub.deployment.tls,
            autoscale=sub.deployment.autoscale,
            runtime=runtime,
            worker_replicas=worker_replicas,
        ),
        llms=LlmConfig(
            enabled_providers=list(sub.llms.enabled_providers),
            roles=LlmRoleAssignment(**sub.llms.roles.model_dump()),
            allow_fallback=sub.llms.allow_fallback,
            monthly_budget_usd=sub.llms.monthly_budget_usd,
        ),
        memory=MemoryConfig(
            driver=sub.memory.driver,
            graph=sub.memory.graph,
            retention_days=sub.memory.retention_days,
            encryption_at_rest=sub.memory.encryption_at_rest,
        ),
        areas=AreasConfig(enabled=list(sub.areas.enabled)),
        governance=GovernanceConfig(
            default_autonomy=sub.governance.default_autonomy,
            kill_switch_enabled=sub.governance.kill_switch_enabled,
            audit_retention_days=sub.governance.audit_retention_days,
            monthly_budget_alert_pct=sub.governance.monthly_budget_alert_pct,
            require_2fa_for_superadmin=sub.governance.require_2fa_for_superadmin,
            auth=auth,
        ),
    )
