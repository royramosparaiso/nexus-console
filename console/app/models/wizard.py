"""Wizard schema — emits nexus.instance.yaml.

Six sections, matching Nexus OS Specs v0.6 §2quater bootstrap payload:
  1. persona
  2. deployment
  3. llms
  4. memory
  5. areas
  6. governance
"""

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.stack import StackConfig


# ---------- Section 1: Persona ----------

PersonaKind = Literal[
    "personal",       # single-user personal instance
    "family",         # household / familia
    "company",        # a company running its own instance
    "community",      # neighbourhood, association, community group
    "client",         # instance operated on behalf of a client
    "custom",
]


class PersonaConfig(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100, description="Public name of this instance's persona.")
    kind: PersonaKind = "personal"
    description: str = Field("", max_length=500)
    default_locale: str = Field("es-ES", pattern=r"^[a-z]{2}-[A-Z]{2}$")


# ---------- Section 2: Deployment ----------

Modality = Literal["local", "fly", "hetzner", "k8s", "onprem", "saas"]


# ---------- Complete-remote payloads ----------

class CompleteRemoteRequest(BaseModel):
    """Sent by the operator after the handoff playbook finished running.

    The operator (or Cloud Cowork / OpenClaw) has already deployed Platform
    at some public endpoint and needs Console to complete the bootstrap
    handshake. If ``endpoint`` is provided, it overrides the endpoint
    stored at wizard-submit time (useful when the real domain differs from
    the placeholder used in the playbook).
    """
    endpoint: Optional[str] = None
    wait_timeout_s: float = 120.0


class CompleteRemoteResult(BaseModel):
    instance_id: UUID
    status: str
    endpoint: str
    platform_version: Optional[str] = None
    error_detail: Optional[str] = None


class DeploymentConfig(BaseModel):
    modality: Modality
    domain: str | None = None                 # e.g. nexus.example.com — optional for local
    region: str | None = None                 # fly region or k8s cluster region
    tls: bool = True
    autoscale: bool = False


# ---------- Section 3: LLMs ----------

LlmProvider = Literal[
    "anthropic", "openai", "openrouter", "perplexity",
    "groq", "together", "mistral", "ollama",
]


class LlmRoleAssignment(BaseModel):
    """Which model powers each router role."""
    planner: str = Field(..., description="High-reasoning model used by orchestrators.")
    coordinator: str = Field(..., description="Mid-tier model for area coordinators.")
    worker: str = Field(..., description="Cheap/fast model for high-volume worker agents.")
    embeddings: str = Field(..., description="Embedding model for memory + retrieval.")


class LlmConfig(BaseModel):
    enabled_providers: list[LlmProvider] = Field(..., min_length=1)
    roles: LlmRoleAssignment
    allow_fallback: bool = True
    monthly_budget_usd: float = Field(50.0, ge=0)


# ---------- Section 4: Memory ----------

MemoryDriver = Literal["sqlite", "postgres", "postgres_pgvector"]
GraphDriver = Literal["none", "neo4j", "postgres_graph"]


class MemoryConfig(BaseModel):
    driver: MemoryDriver = "postgres_pgvector"
    graph: GraphDriver = "none"
    retention_days: int = Field(365, ge=7, le=3650)
    encryption_at_rest: bool = True


# ---------- Section 5: Areas ----------

# Slugs match `area:{slug}` scopes in Specs §2ter.5.
AVAILABLE_AREAS: list[dict] = [
    {"slug": "personal_organization", "label": "Personal organization", "tier": "core", "default": True},
    {"slug": "meetings", "label": "Meetings & action items", "tier": "core", "default": True},
    {"slug": "finance_personal", "label": "Personal finance", "tier": "core", "default": True},
    {"slug": "comms", "label": "Communications", "tier": "core", "default": True},
    {"slug": "brand", "label": "Brand & marketing", "tier": "vertical", "default": False},
    {"slug": "sales", "label": "Sales & pipeline", "tier": "vertical", "default": False},
    {"slug": "product", "label": "Product & roadmap", "tier": "vertical", "default": False},
    {"slug": "dev", "label": "Dev (agent factory local)", "tier": "vertical", "default": False},
    {"slug": "legal", "label": "Legal & compliance", "tier": "vertical", "default": False},
    {"slug": "operations", "label": "Operations", "tier": "vertical", "default": False},
]


class AreasConfig(BaseModel):
    enabled: list[str] = Field(..., min_length=1)

    @field_validator("enabled")
    @classmethod
    def _valid_slugs(cls, v: list[str]) -> list[str]:
        allowed = {a["slug"] for a in AVAILABLE_AREAS}
        bad = [s for s in v if s not in allowed]
        if bad:
            raise ValueError(f"unknown area slugs: {bad}")
        return v


# ---------- Section 6: Governance ----------

AutonomyLevel = Literal["read_only", "propose", "act_with_approval", "act_autonomously"]


class GovernanceConfig(BaseModel):
    default_autonomy: AutonomyLevel = "act_with_approval"
    kill_switch_enabled: bool = True
    audit_retention_days: int = Field(730, ge=90, le=3650)
    monthly_budget_alert_pct: int = Field(80, ge=10, le=100)
    require_2fa_for_superadmin: bool = True


# ---------- Complete wizard payload ----------

class WizardSubmission(BaseModel):
    instance_name: str = Field(..., min_length=1, max_length=100, description="Internal slug/name of the instance.")
    persona: PersonaConfig
    deployment: DeploymentConfig
    llms: LlmConfig
    memory: MemoryConfig
    areas: AreasConfig
    governance: GovernanceConfig
    # Optional — legacy submissions without a stack section still validate.
    stack: Optional[StackConfig] = None


class WizardPreview(BaseModel):
    yaml: str
    warnings: list[str] = Field(default_factory=list)


class WizardSubmitResult(BaseModel):
    instance_id: UUID
    status: str
    yaml_path: str
    next_steps: list[str]
