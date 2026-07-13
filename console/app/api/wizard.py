"""Wizard endpoints — persists an Instance, provisions Platform, dispatches bootstrap."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import SessionLocal, get_db
from app.models.db import InstanceRow
from app.models.wizard import (
    AVAILABLE_AREAS,
    WizardPreview,
    WizardSubmission,
    WizardSubmitResult,
)
from app.services.bootstrap_client import (
    BootstrapError, dispatch_bootstrap, wait_healthy,
)
from app.services.deployer import (
    DeployerError, provision_local, start_compose,
)
from app.services.keypair import get_or_create_keypair
from app.services.manifest import submission_to_manifest
from app.services.wizard_yaml import compute_warnings, default_areas, render_instance_yaml

router = APIRouter()


@router.get("/schema")
async def wizard_schema():
    """Front-end fetches this once to render forms."""
    return {
        "steps": [
            {"id": "persona", "label": "Persona"},
            {"id": "deployment", "label": "Deployment"},
            {"id": "llms", "label": "LLM providers"},
            {"id": "memory", "label": "Memory & graph"},
            {"id": "areas", "label": "Active areas"},
            {"id": "governance", "label": "Governance"},
        ],
        "persona_kinds": [
            {"value": "personal", "label": "Personal (single user)"},
            {"value": "family", "label": "Family / household"},
            {"value": "company", "label": "Company"},
            {"value": "community", "label": "Community / association"},
            {"value": "client", "label": "Client engagement"},
            {"value": "custom", "label": "Custom"},
        ],
        "modalities": [
            {"value": "local", "label": "Local (Docker Compose)"},
            {"value": "fly", "label": "Fly.io"},
            {"value": "k8s", "label": "Kubernetes"},
            {"value": "onprem", "label": "On-premise"},
            {"value": "saas", "label": "Managed SaaS (hosted by operator)"},
        ],
        "agent_runtimes": [
            {"value": "in_process", "label": "In-process (default; simplest)"},
            {"value": "redis_workers", "label": "Redis workers (v0.7 — reserved)"},
        ],
        "llm_providers": [
            "anthropic", "openai", "openrouter", "perplexity",
            "groq", "together", "mistral", "ollama",
        ],
        "auth_providers": [
            {"value": "password_totp", "label": "Password + TOTP (offline)"},
            {"value": "magic_link", "label": "Magic link (email)"},
            {"value": "oauth_google", "label": "Google OAuth"},
            {"value": "oauth_microsoft", "label": "Microsoft OAuth"},
            {"value": "oauth_github", "label": "GitHub OAuth"},
            {"value": "console_idp", "label": "Console IdP (cross-instance)"},
            {"value": "clerk", "label": "Clerk (SaaS auth)"},
        ],
        "memory_drivers": [
            {"value": "sqlite", "label": "SQLite (single-file, local only)"},
            {"value": "postgres", "label": "Postgres (no vector search)"},
            {"value": "postgres_pgvector", "label": "Postgres + pgvector (recommended)"},
        ],
        "graph_drivers": [
            {"value": "none", "label": "No graph"},
            {"value": "neo4j", "label": "Neo4j"},
            {"value": "postgres_graph", "label": "Postgres graph extension"},
        ],
        "autonomy_levels": [
            {"value": "read_only", "label": "Read-only"},
            {"value": "propose", "label": "Propose (user must accept)"},
            {"value": "act_with_approval", "label": "Act with approval"},
            {"value": "act_autonomously", "label": "Act autonomously"},
        ],
        "available_areas": AVAILABLE_AREAS,
        "defaults": {
            "persona": {
                "display_name": "",
                "kind": "personal",
                "description": "",
                "default_locale": "es-ES",
            },
            "deployment": {
                "modality": "local",
                "domain": None,
                "region": None,
                "tls": True,
                "autoscale": False,
                "runtime": "in_process",
                "worker_replicas": 1,
            },
            "llms": {
                "enabled_providers": ["anthropic", "openai"],
                "roles": {
                    "planner": "claude-opus-4-8",
                    "coordinator": "claude-sonnet-4-6",
                    "worker": "gpt-5-mini",
                    "embeddings": "text-embedding-3-large",
                },
                "allow_fallback": True,
                "monthly_budget_usd": 50.0,
            },
            "memory": {
                "driver": "postgres_pgvector",
                "graph": "none",
                "retention_days": 365,
                "encryption_at_rest": True,
            },
            "areas": {"enabled": default_areas()},
            "governance": {
                "default_autonomy": "act_with_approval",
                "kill_switch_enabled": True,
                "audit_retention_days": 730,
                "monthly_budget_alert_pct": 80,
                "require_2fa_for_superadmin": True,
                "auth": {"provider": "password_totp"},
            },
        },
    }


@router.post("/preview", response_model=WizardPreview)
async def wizard_preview(sub: WizardSubmission):
    yaml = render_instance_yaml(sub)
    warnings = compute_warnings(sub)
    return WizardPreview(yaml=yaml, warnings=warnings)


@router.post("/submit", response_model=WizardSubmitResult)
async def wizard_submit(
    sub: WizardSubmission,
    background: BackgroundTasks,
    dry_run: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Persist the instance, provision Platform (compose files), dispatch bootstrap.

    Parameters:
      dry_run: if true, write compose files but do NOT start containers nor
        call /_bootstrap. Used by tests and by the CLI preview flow.
    """
    manifest = submission_to_manifest(sub)
    yaml = render_instance_yaml(sub)

    row = InstanceRow(
        name=sub.instance_name,
        persona_kind=sub.persona.kind,
        persona_display_name=sub.persona.display_name,
        modality=sub.deployment.modality,
        agent_runtime=manifest.deployment.runtime,
        auth_provider=manifest.governance.auth.provider,
        manifest_json=manifest.model_dump(mode="json"),
        status="bootstrap-pending",
    )
    db.add(row)
    await db.flush()  # get id

    # Persist YAML on disk (nice for humans + operators)
    yaml_dir = settings.data_dir / "instances" / str(row.id)
    yaml_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = yaml_dir / "nexus.instance.yaml"
    yaml_path.write_text(yaml, encoding="utf-8")
    row.yaml_path = str(yaml_path)

    # Provision Platform based on modality
    if sub.deployment.modality == "local":
        try:
            compose_dir, token, endpoint = provision_local(row.id)
        except DeployerError as e:
            raise HTTPException(status_code=500, detail=str(e))
        row.bootstrap_token = token
        row.compose_dir = str(compose_dir)
        row.endpoint = endpoint
        next_steps = [
            f"Compose files written to {compose_dir}",
            f"docker compose up -d && wait for /_health at {endpoint}",
            f"Console will POST /_bootstrap with the manifest and burn the token",
        ]
    else:
        row.status = "unsupported"
        row.error_detail = f"modality '{sub.deployment.modality}' not yet implemented in v0.6"
        next_steps = [
            f"Only 'local' modality is functional in v0.6. Requested: {sub.deployment.modality}",
        ]
        await db.commit()
        return WizardSubmitResult(
            instance_id=row.id, status=row.status,
            yaml_path=str(yaml_path), next_steps=next_steps,
        )

    await db.commit()

    if not dry_run:
        # Fire-and-forget: start compose + wait health + dispatch bootstrap
        background.add_task(_deploy_and_bootstrap, row.id)

    return WizardSubmitResult(
        instance_id=row.id, status=row.status,
        yaml_path=str(yaml_path), next_steps=next_steps,
    )


async def _deploy_and_bootstrap(instance_id) -> None:
    """Background: start Compose, wait health, dispatch bootstrap. Own session."""
    async with SessionLocal() as db:
        row = await db.get(InstanceRow, instance_id)
        if row is None:
            return
        try:
            if row.compose_dir:
                start_compose(Path(row.compose_dir))
        except DeployerError as e:
            row.status = "deploy-failed"
            row.error_detail = str(e)
            await db.commit()
            return

        try:
            await wait_healthy(row.endpoint, timeout_s=120.0)
        except BootstrapError as e:
            row.status = "bootstrap-failed"
            row.error_detail = str(e)
            await db.commit()
            return

        kp = await get_or_create_keypair(db)
        from nexus_core.models import InstanceManifest
        manifest = InstanceManifest.model_validate(row.manifest_json)
        webhook = f"http://console:7000/_platform/notify"  # Console container name
        try:
            await dispatch_bootstrap(
                db=db, row=row, endpoint=row.endpoint,
                token=row.bootstrap_token,
                console_kp=kp, manifest=manifest, webhook_url=webhook,
            )
        except BootstrapError as e:
            row.status = "bootstrap-failed"
            row.error_detail = str(e)
            await db.commit()
