"""Wizard endpoints — emits nexus.instance.yaml and registers the instance."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.instances import InstanceOut, _REGISTRY
from app.models.wizard import (
    AVAILABLE_AREAS,
    WizardPreview,
    WizardSubmission,
    WizardSubmitResult,
)
from app.services.wizard_yaml import compute_warnings, default_areas, render_instance_yaml

router = APIRouter()


@router.get("/schema")
async def wizard_schema():
    """Front-end fetches this once to render forms.

    Returns metadata about steps, available options and sensible defaults.
    """
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
        "llm_providers": [
            "anthropic", "openai", "openrouter", "perplexity",
            "groq", "together", "mistral", "ollama",
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
            },
        },
    }


@router.post("/preview", response_model=WizardPreview)
async def wizard_preview(sub: WizardSubmission):
    yaml = render_instance_yaml(sub)
    warnings = compute_warnings(sub)
    return WizardPreview(yaml=yaml, warnings=warnings)


@router.post("/submit", response_model=WizardSubmitResult)
async def wizard_submit(sub: WizardSubmission):
    # Compute warnings — do NOT block on warnings, only on validation errors (handled by Pydantic).
    yaml = render_instance_yaml(sub)

    # Persist YAML to disk under console/instance/{iid}/nexus.instance.yaml
    iid = uuid4()
    root = Path("./console/instance") / str(iid)
    try:
        root.mkdir(parents=True, exist_ok=True)
        yaml_path = root / "nexus.instance.yaml"
        yaml_path.write_text(yaml, encoding="utf-8")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"failed to persist yaml: {e}")

    # Register in in-memory registry (will move to Postgres)
    instance = InstanceOut(
        instance_id=iid,
        name=sub.instance_name,
        persona_display_name=sub.persona.display_name,
        modality=sub.deployment.modality,
        endpoint=None,
        version=None,
        status="bootstrap-pending",
        created_at=datetime.now(timezone.utc),
    )
    _REGISTRY[iid] = instance

    next_steps = [
        "Console will dispatch a signed `bootstrap` request to a fresh Platform.",
        "Once Platform ACKs, it becomes 'running' in the registry.",
        f"Configure secrets for {', '.join(sub.llms.enabled_providers)} in LLM Providers.",
    ]
    return WizardSubmitResult(
        instance_id=iid,
        status="bootstrap-pending",
        yaml_path=str(yaml_path),
        next_steps=next_steps,
    )
