"""Stack catalogue + recommender.

Nexus OS is bring-your-own-services: the wizard picks which managed
service fills each infrastructure role. This module owns

  1. The canonical *catalogue* of services we know how to hand off to
     (via OpenClaw / Cloud Cowork playbooks).
  2. A pure recommender that turns operator preferences (budget, cloud
     vs. local, feature needs) into a concrete ``StackSelection``.

Everything here is data + pure functions — persistence lives in
``wizard`` and rendering lives in ``services/wizard_yaml.py``.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.host_capabilities import HostCapabilities


# ---------------------------------------------------------------------------
# Roles — what a service *does* in the stack.
# ---------------------------------------------------------------------------

StackRole = Literal[
    "app_compute",         # Console + Platform runtime
    "frontend_hosting",    # static/edge hosting for Console web
    "postgres",            # OLTP + pgvector fallback
    "graph_db",            # Neo4j / Memgraph / Kuzu embedded
    "vector_db",           # Qdrant / Turbopuffer / Pinecone / pgvector
    "cache_queue",         # Redis + queues
    "gpu_serverless",      # Kokoro voice, embeddings, custom inference
    "llm_gateway",         # unified LLM API (OpenRouter, etc.)
    "object_storage",      # S3-compatible blob store
    "auth",                # user auth / SSO
    "dns_cdn",             # DNS, CDN, WAF
    "error_monitoring",    # Sentry-style
    "log_platform",        # structured logs / observability
    "product_analytics",   # PostHog-style
    "llm_observability",   # Langfuse-style, agent traces + evals
    "email_transactional", # Resend / Postmark
    "background_jobs",     # Trigger.dev / Inngest / QStash
    "ci_cd",               # GitHub Actions / GitLab CI
]


# Budget tiers a service can appear in. A single service can belong to
# more than one tier (e.g. Neon has both Free and Launch plans).
BudgetTier = Literal["free", "hobby", "standard", "scale"]


DeploymentMode = Literal["local", "cloud", "hybrid"]


# ---------------------------------------------------------------------------
# Service catalogue entry.
# ---------------------------------------------------------------------------


class StackService(BaseModel):
    """One managed service we can hand off to.

    ``slug`` is stable and used everywhere (YAML, playbook lookup, UI).
    ``name`` / ``vendor`` are human-facing. Prices are USD/month and
    intentionally coarse — they drive the recommender, not billing.
    """

    slug: str = Field(..., pattern=r"^[a-z0-9_]+$")
    name: str
    vendor: str
    role: StackRole
    tiers: list[BudgetTier]
    # Coarse price bands so the recommender can compare apples to apples.
    price_free_usd: float = 0.0      # what the free tier costs (usually 0)
    price_entry_usd: float = 0.0     # first paid tier
    price_scale_usd: float = 0.0     # a representative scale tier
    self_hostable: bool = False
    scale_to_zero: bool = False
    open_source: bool = False
    homepage: str
    notes: str = ""
    # Which handoff playbook automates provisioning + credential capture.
    handoff_playbook: str | None = None


# ---------------------------------------------------------------------------
# Catalogue — single source of truth.
# ---------------------------------------------------------------------------

CATALOGUE: list[StackService] = [
    # ---- App compute ----
    StackService(
        slug="railway",
        name="Railway",
        vendor="Railway Corp.",
        role="app_compute",
        tiers=["hobby", "standard"],
        price_entry_usd=5.0,
        price_scale_usd=20.0,
        homepage="https://railway.com/pricing",
        notes="Git-push deploys, private mesh, best DX for multi-service.",
        handoff_playbook="railway-project",
    ),
    StackService(
        slug="fly",
        name="Fly.io",
        vendor="Fly.io",
        role="app_compute",
        tiers=["hobby", "standard", "scale"],
        price_entry_usd=5.0,
        price_scale_usd=30.0,
        scale_to_zero=True,
        homepage="https://fly.io/docs/about/pricing/",
        notes="Global regions, GPU add-ons, per-second billing, scale-to-zero.",
        handoff_playbook="fly-app",
    ),
    StackService(
        slug="render",
        name="Render",
        vendor="Render",
        role="app_compute",
        tiers=["hobby", "standard"],
        price_entry_usd=7.0,
        price_scale_usd=25.0,
        homepage="https://render.com/pricing",
        notes="Simple PaaS, per-service pricing; excluded from v0.7 stack policy.",
        handoff_playbook="render-service",
    ),
    StackService(
        slug="northflank",
        name="Northflank",
        vendor="Northflank",
        role="app_compute",
        tiers=["standard", "scale"],
        price_entry_usd=15.0,
        price_scale_usd=60.0,
        homepage="https://northflank.com/pricing",
        notes="Container-native, good for microservices at scale.",
        handoff_playbook="northflank-project",
    ),
    StackService(
        slug="hetzner_cx22",
        name="Hetzner CX22",
        vendor="Hetzner Cloud",
        role="app_compute",
        tiers=["free", "hobby"],
        price_entry_usd=5.0,
        price_scale_usd=20.0,
        self_hostable=True,
        homepage="https://hetzner.com/cloud",
        notes="Cheapest EU VPS; you run docker compose. Playbook covers it.",
        handoff_playbook="hetzner-compose",
    ),

    # ---- Frontend hosting ----
    StackService(
        slug="vercel",
        name="Vercel",
        vendor="Vercel",
        role="frontend_hosting",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=20.0,
        homepage="https://vercel.com/pricing",
        notes="Free Hobby covers 100 GB bandwidth; Pro when you need SLA.",
        handoff_playbook="vercel-project",
    ),
    StackService(
        slug="cloudflare_pages",
        name="Cloudflare Pages",
        vendor="Cloudflare",
        role="frontend_hosting",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=20.0,
        homepage="https://pages.cloudflare.com",
        notes="Free unlimited bandwidth; pairs with Workers for edge functions.",
        handoff_playbook="cloudflare-pages",
    ),
    StackService(
        slug="netlify",
        name="Netlify",
        vendor="Netlify",
        role="frontend_hosting",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=19.0,
        homepage="https://netlify.com/pricing",
        handoff_playbook="netlify-site",
    ),

    # ---- Postgres ----
    StackService(
        slug="neon",
        name="Neon",
        vendor="Neon",
        role="postgres",
        tiers=["free", "hobby", "standard", "scale"],
        price_entry_usd=19.0,
        price_scale_usd=69.0,
        scale_to_zero=True,
        open_source=True,
        homepage="https://neon.com/pricing",
        notes="Branching-per-Git-branch is unique; serverless Postgres.",
        handoff_playbook="neon-project",
    ),
    StackService(
        slug="supabase",
        name="Supabase",
        vendor="Supabase",
        role="postgres",
        tiers=["free", "hobby", "standard", "scale"],
        price_entry_usd=0.0,
        price_scale_usd=125.0,
        open_source=True,
        homepage="https://supabase.com/pricing",
        notes="Postgres + Auth + Storage + Realtime + pgvector in one plan.",
        handoff_playbook="supabase-project",
    ),
    StackService(
        slug="fly_postgres",
        name="Fly Postgres",
        vendor="Fly.io",
        role="postgres",
        tiers=["hobby", "standard"],
        price_entry_usd=8.0,
        price_scale_usd=40.0,
        self_hostable=True,
        open_source=True,
        homepage="https://fly.io/docs/postgres/",
        notes="Cheap but unmanaged — you own backups + upgrades.",
        handoff_playbook="fly-postgres",
    ),
    StackService(
        slug="local_postgres",
        name="Local Postgres (Docker)",
        vendor="PostgreSQL",
        role="postgres",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://postgresql.org",
        notes="For local modality only.",
    ),

    # ---- Graph DB ----
    StackService(
        slug="neo4j_aura",
        name="Neo4j AuraDB",
        vendor="Neo4j",
        role="graph_db",
        tiers=["free", "standard", "scale"],
        price_entry_usd=65.0,
        price_scale_usd=200.0,
        open_source=True,
        homepage="https://neo4j.com/pricing/",
        notes="Free: 200k nodes / 400k rels. Pro when you outgrow it.",
        handoff_playbook="neo4j-aura",
    ),
    StackService(
        slug="memgraph_cloud",
        name="Memgraph Cloud",
        vendor="Memgraph",
        role="graph_db",
        tiers=["standard", "scale"],
        price_entry_usd=40.0,
        price_scale_usd=150.0,
        open_source=True,
        homepage="https://memgraph.com/cloud",
        notes="Cypher-compatible, faster than Neo4j on some workloads.",
        handoff_playbook="memgraph-cloud",
    ),
    StackService(
        slug="kuzu_embedded",
        name="Kuzu (embedded)",
        vendor="Kuzu Inc.",
        role="graph_db",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://kuzudb.com",
        notes="Embedded graph DB — zero ops if graph fits on one node.",
    ),

    # ---- Vector DB ----
    StackService(
        slug="qdrant_cloud",
        name="Qdrant Cloud",
        vendor="Qdrant",
        role="vector_db",
        tiers=["free", "standard", "scale"],
        price_entry_usd=25.0,
        price_scale_usd=100.0,
        self_hostable=True,
        open_source=True,
        homepage="https://qdrant.tech/pricing/",
        notes="Free 1 GB; best FOSS vector DB with a real managed tier.",
        handoff_playbook="qdrant-cluster",
    ),
    StackService(
        slug="turbopuffer",
        name="Turbopuffer",
        vendor="Turbopuffer",
        role="vector_db",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=25.0,
        homepage="https://turbopuffer.com/pricing",
        notes="Serverless vectors on S3; cheapest at scale, cold-start noticeable.",
        handoff_playbook="turbopuffer-workspace",
    ),
    StackService(
        slug="pinecone",
        name="Pinecone",
        vendor="Pinecone",
        role="vector_db",
        tiers=["free", "standard", "scale"],
        price_entry_usd=70.0,
        price_scale_usd=300.0,
        homepage="https://pinecone.io/pricing/",
        handoff_playbook="pinecone-index",
    ),
    StackService(
        slug="pgvector",
        name="pgvector (on Postgres)",
        vendor="PostgreSQL",
        role="vector_db",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://github.com/pgvector/pgvector",
        notes="Uses your Postgres; fine up to ~1M vectors.",
    ),

    # ---- Cache / queue ----
    StackService(
        slug="upstash",
        name="Upstash Redis + QStash",
        vendor="Upstash",
        role="cache_queue",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=10.0,
        scale_to_zero=True,
        homepage="https://upstash.com/pricing",
        notes="Pay-per-request Redis + serverless message queue.",
        handoff_playbook="upstash-redis",
    ),
    StackService(
        slug="redis_cloud",
        name="Redis Cloud",
        vendor="Redis Ltd.",
        role="cache_queue",
        tiers=["free", "standard", "scale"],
        price_entry_usd=7.0,
        price_scale_usd=50.0,
        open_source=True,
        homepage="https://redis.com/cloud/",
        handoff_playbook="redis-cloud",
    ),
    StackService(
        slug="local_redis",
        name="Local Redis (Docker)",
        vendor="Redis",
        role="cache_queue",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://redis.io",
    ),

    # ---- GPU serverless ----
    StackService(
        slug="modal",
        name="Modal",
        vendor="Modal Labs",
        role="gpu_serverless",
        tiers=["free", "standard", "scale"],
        price_entry_usd=0.0,
        price_scale_usd=30.0,
        scale_to_zero=True,
        homepage="https://modal.com/pricing",
        notes="$30/mo credit, sub-second cold starts, best DX for Kokoro + evals.",
        handoff_playbook="modal-app",
    ),
    StackService(
        slug="runpod_serverless",
        name="RunPod Serverless",
        vendor="RunPod",
        role="gpu_serverless",
        tiers=["standard", "scale"],
        price_entry_usd=5.0,
        price_scale_usd=50.0,
        scale_to_zero=True,
        homepage="https://runpod.io/pricing",
        notes="Cheaper $/GPU-hour than Modal; worse cold-start.",
        handoff_playbook="runpod-endpoint",
    ),
    StackService(
        slug="replicate",
        name="Replicate",
        vendor="Replicate",
        role="gpu_serverless",
        tiers=["standard"],
        price_entry_usd=10.0,
        price_scale_usd=100.0,
        homepage="https://replicate.com/pricing",
        notes="Best when you use off-the-shelf public models.",
        handoff_playbook="replicate-model",
    ),
    StackService(
        slug="fly_gpu",
        name="Fly GPU (A10)",
        vendor="Fly.io",
        role="gpu_serverless",
        tiers=["standard"],
        price_entry_usd=15.0,
        price_scale_usd=60.0,
        scale_to_zero=True,
        homepage="https://fly.io/docs/gpus/",
        handoff_playbook="fly-gpu-app",
    ),

    # ---- LLM gateway ----
    StackService(
        slug="openrouter",
        name="OpenRouter",
        vendor="OpenRouter",
        role="llm_gateway",
        tiers=["standard"],
        price_entry_usd=0.0,
        price_scale_usd=0.0,
        homepage="https://openrouter.ai/",
        notes="Pass-through to 300+ models; small margin over provider prices.",
        handoff_playbook="openrouter-key",
    ),
    StackService(
        slug="litellm_proxy",
        name="LiteLLM Proxy (self-host)",
        vendor="BerriAI",
        role="llm_gateway",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://litellm.ai/",
        notes="Self-host a routing layer; no per-request margin.",
    ),

    # ---- Object storage ----
    StackService(
        slug="cloudflare_r2",
        name="Cloudflare R2",
        vendor="Cloudflare",
        role="object_storage",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=5.0,
        homepage="https://developers.cloudflare.com/r2/pricing/",
        notes="Zero egress fees — enormous over time vs S3.",
        handoff_playbook="cloudflare-r2-bucket",
    ),
    StackService(
        slug="backblaze_b2",
        name="Backblaze B2",
        vendor="Backblaze",
        role="object_storage",
        tiers=["free", "standard"],
        price_entry_usd=6.0,
        price_scale_usd=30.0,
        homepage="https://backblaze.com/cloud-storage/pricing",
        handoff_playbook="backblaze-b2-bucket",
    ),
    StackService(
        slug="aws_s3",
        name="AWS S3",
        vendor="Amazon",
        role="object_storage",
        tiers=["standard", "scale"],
        price_entry_usd=5.0,
        price_scale_usd=50.0,
        homepage="https://aws.amazon.com/s3/pricing/",
        notes="Egress fees; only worth it if you're already deep in AWS.",
        handoff_playbook="aws-s3-bucket",
    ),

    # ---- Auth ----
    StackService(
        slug="clerk",
        name="Clerk",
        vendor="Clerk",
        role="auth",
        tiers=["free", "standard"],
        price_entry_usd=25.0,
        price_scale_usd=100.0,
        homepage="https://clerk.com/pricing",
        notes="Free up to 10k MAU; best DX drop-in auth.",
        handoff_playbook="clerk-app",
    ),
    StackService(
        slug="workos",
        name="WorkOS AuthKit",
        vendor="WorkOS",
        role="auth",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=125.0,
        homepage="https://workos.com/pricing",
        notes="Free up to 1M MAU; SSO/SCIM add-ons cost extra.",
        handoff_playbook="workos-tenant",
    ),
    StackService(
        slug="better_auth",
        name="Better-Auth (self-host)",
        vendor="Better-Auth",
        role="auth",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://better-auth.com",
        notes="Own your auth tables; no per-MAU pricing.",
    ),

    # ---- DNS + CDN ----
    StackService(
        slug="cloudflare",
        name="Cloudflare (DNS + WAF)",
        vendor="Cloudflare",
        role="dns_cdn",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=20.0,
        homepage="https://cloudflare.com",
        notes="Free tier is best-in-class.",
        handoff_playbook="cloudflare-zone",
    ),

    # ---- Error monitoring ----
    StackService(
        slug="sentry",
        name="Sentry",
        vendor="Sentry",
        role="error_monitoring",
        tiers=["free", "standard"],
        price_entry_usd=26.0,
        price_scale_usd=80.0,
        open_source=True,
        homepage="https://sentry.io/pricing/",
        handoff_playbook="sentry-project",
    ),
    StackService(
        slug="glitchtip",
        name="GlitchTip (self-host)",
        vendor="GlitchTip",
        role="error_monitoring",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://glitchtip.com",
        notes="Sentry-compatible SDK, free if self-hosted.",
    ),

    # ---- Log platform ----
    StackService(
        slug="axiom",
        name="Axiom",
        vendor="Axiom",
        role="log_platform",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=25.0,
        homepage="https://axiom.co/pricing",
        notes="500 GB/mo free; much cheaper than Datadog.",
        handoff_playbook="axiom-dataset",
    ),
    StackService(
        slug="better_stack",
        name="Better Stack Logs",
        vendor="Better Stack",
        role="log_platform",
        tiers=["free", "standard"],
        price_entry_usd=25.0,
        price_scale_usd=100.0,
        homepage="https://betterstack.com/logs",
        handoff_playbook="betterstack-source",
    ),
    StackService(
        slug="loki_self_host",
        name="Grafana Loki (self-host)",
        vendor="Grafana Labs",
        role="log_platform",
        tiers=["free"],
        self_hostable=True,
        open_source=True,
        homepage="https://grafana.com/oss/loki/",
    ),
    StackService(
        slug="grafana_cloud",
        name="Grafana Cloud",
        vendor="Grafana Labs",
        role="log_platform",
        tiers=["free", "hobby", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=29.0,
        homepage="https://grafana.com/products/cloud/",
        notes="50 GB logs + 10k series metrics + 50 GB traces on the free tier.",
        handoff_playbook="grafana-cloud-stack",
    ),

    # ---- Product analytics ----
    StackService(
        slug="posthog",
        name="PostHog Cloud",
        vendor="PostHog",
        role="product_analytics",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=50.0,
        self_hostable=True,
        open_source=True,
        homepage="https://posthog.com/pricing",
        notes="Analytics + session replay + flags + A/B tests in one.",
        handoff_playbook="posthog-project",
    ),
    StackService(
        slug="plausible",
        name="Plausible",
        vendor="Plausible",
        role="product_analytics",
        tiers=["standard"],
        price_entry_usd=9.0,
        price_scale_usd=19.0,
        self_hostable=True,
        open_source=True,
        homepage="https://plausible.io/",
        notes="Web-only, privacy-first, no session replay.",
        handoff_playbook="plausible-site",
    ),

    # ---- LLM observability ----
    StackService(
        slug="langfuse",
        name="Langfuse Cloud",
        vendor="Langfuse",
        role="llm_observability",
        tiers=["free", "standard", "scale"],
        price_entry_usd=0.0,
        price_scale_usd=59.0,
        self_hostable=True,
        open_source=True,
        homepage="https://langfuse.com/pricing",
        notes="Agent traces + evals + prompt versioning. 50k events free.",
        handoff_playbook="langfuse-project",
    ),
    StackService(
        slug="langsmith",
        name="LangSmith",
        vendor="LangChain",
        role="llm_observability",
        tiers=["free", "standard"],
        price_entry_usd=39.0,
        price_scale_usd=99.0,
        homepage="https://smith.langchain.com/",
        handoff_playbook="langsmith-project",
    ),

    # ---- Email transactional ----
    StackService(
        slug="resend",
        name="Resend",
        vendor="Resend",
        role="email_transactional",
        tiers=["free", "standard"],
        price_entry_usd=20.0,
        price_scale_usd=90.0,
        homepage="https://resend.com/pricing",
        notes="3k emails/mo free; excellent DX.",
        handoff_playbook="resend-domain",
    ),
    StackService(
        slug="postmark",
        name="Postmark",
        vendor="ActiveCampaign",
        role="email_transactional",
        tiers=["standard"],
        price_entry_usd=15.0,
        price_scale_usd=50.0,
        homepage="https://postmarkapp.com/pricing",
        handoff_playbook="postmark-server",
    ),

    # ---- Background jobs ----
    StackService(
        slug="trigger_dev",
        name="Trigger.dev Cloud",
        vendor="Trigger.dev",
        role="background_jobs",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=20.0,
        self_hostable=True,
        open_source=True,
        homepage="https://trigger.dev/pricing",
        notes="Long-running jobs with retry + observability. Free 10k runs.",
        handoff_playbook="trigger-project",
    ),
    StackService(
        slug="inngest",
        name="Inngest",
        vendor="Inngest",
        role="background_jobs",
        tiers=["free", "standard"],
        price_entry_usd=20.0,
        price_scale_usd=50.0,
        homepage="https://inngest.com/pricing",
        handoff_playbook="inngest-app",
    ),

    # ---- CI/CD ----
    StackService(
        slug="github_actions",
        name="GitHub Actions",
        vendor="GitHub",
        role="ci_cd",
        tiers=["free", "standard"],
        price_entry_usd=0.0,
        price_scale_usd=4.0,
        homepage="https://github.com/features/actions",
        notes="2000 minutes/mo free on private repos.",
        handoff_playbook="github-repo",
    ),
]


CATALOGUE_BY_SLUG: dict[str, StackService] = {s.slug: s for s in CATALOGUE}


def services_for_role(role: StackRole) -> list[StackService]:
    return [s for s in CATALOGUE if s.role == role]


# ---------------------------------------------------------------------------
# Standard 100 EUR/month cloud stack — referenced by the recommender when
# the operator has ~100 EUR (~110 USD) to spend and does NOT want local.
# ---------------------------------------------------------------------------

STANDARD_100_EUR_STACK: dict[StackRole, str] = {
    "app_compute":         "railway",
    "frontend_hosting":    "vercel",
    "postgres":            "neon",
    "graph_db":            "neo4j_aura",
    "vector_db":           "qdrant_cloud",
    "cache_queue":         "upstash",
    "gpu_serverless":      "modal",
    "llm_gateway":         "openrouter",
    "object_storage":      "cloudflare_r2",
    "auth":                "clerk",
    "dns_cdn":             "cloudflare",
    "error_monitoring":    "sentry",
    "log_platform":        "axiom",
    "product_analytics":   "posthog",
    "llm_observability":   "langfuse",
    "email_transactional": "resend",
    "background_jobs":     "trigger_dev",
    "ci_cd":               "github_actions",
}


# ---------------------------------------------------------------------------
# Recommender input — what the wizard asks the operator.
# ---------------------------------------------------------------------------


class StackPreferences(BaseModel):
    """Answers from the initial cost-vs-power questionnaire."""

    monthly_budget_eur: float = Field(100.0, ge=0, le=10_000)
    deployment_mode: DeploymentMode = "cloud"
    team_size: int = Field(4, ge=1, le=10_000)
    # Feature flags — turn optional roles on/off.
    needs_graph_db: bool = True
    needs_voice_gpu: bool = True
    needs_llm_observability: bool = True
    needs_product_analytics: bool = True
    needs_background_jobs: bool = True
    # Preferences.
    prefer_open_source: bool = False
    prefer_scale_to_zero: bool = True
    region: str = "eu"


class StackSelection(BaseModel):
    """Concrete choice — one service per included role."""

    services: dict[StackRole, str] = Field(default_factory=dict)
    estimated_monthly_usd: float = 0.0
    tier: BudgetTier = "standard"
    rationale: str = ""

    @field_validator("services")
    @classmethod
    def _known_slugs(cls, v: dict[StackRole, str]) -> dict[StackRole, str]:
        for role, slug in v.items():
            svc = CATALOGUE_BY_SLUG.get(slug)
            if svc is None:
                raise ValueError(f"unknown service slug: {slug}")
            if svc.role != role:
                raise ValueError(
                    f"service {slug!r} has role {svc.role!r}, not {role!r}"
                )
        return v


# ---------------------------------------------------------------------------
# Recommender.
# ---------------------------------------------------------------------------


# Roles that are always included regardless of feature flags.
_CORE_ROLES: set[StackRole] = {
    "app_compute", "frontend_hosting", "postgres", "vector_db",
    "cache_queue", "llm_gateway", "object_storage", "dns_cdn", "ci_cd",
}

# Feature-flagged roles — each maps to the pref attribute that gates it.
_OPTIONAL_ROLES: dict[StackRole, str] = {
    "graph_db":           "needs_graph_db",
    "gpu_serverless":     "needs_voice_gpu",
    "auth":               "needs_llm_observability",  # keep auth on by default
    "llm_observability":  "needs_llm_observability",
    "product_analytics":  "needs_product_analytics",
    "background_jobs":    "needs_background_jobs",
    "error_monitoring":   "needs_product_analytics",  # bundle with analytics tier
    "log_platform":       "needs_product_analytics",
    "email_transactional": "needs_background_jobs",
}


def _tier_from_budget(budget_eur: float) -> BudgetTier:
    if budget_eur <= 15:
        return "free"
    if budget_eur <= 40:
        return "hobby"
    if budget_eur <= 150:
        return "standard"
    return "scale"


def _pick_for_role(
    role: StackRole,
    prefs: StackPreferences,
    tier: BudgetTier,
) -> StackService | None:
    """Choose the best service for one role given tier + preferences.

    Selection is a small waterfall: local mode → self-hostable; standard
    tier → the 100-EUR canonical pick; free/hobby → cheapest that still
    fits the tier and honours the open-source preference when set.
    """
    candidates = services_for_role(role)
    if not candidates:
        return None

    if prefs.deployment_mode == "local":
        local = [s for s in candidates if s.self_hostable]
        if local:
            # Prefer explicit "local_*" slugs for OLTP/cache; otherwise
            # the first self-hostable option.
            for pref in ("local_postgres", "local_redis", "kuzu_embedded",
                         "pgvector", "litellm_proxy", "better_auth"):
                for s in local:
                    if s.slug == pref:
                        return s
            return local[0]
        # No self-hostable option for this role — skip it in local mode.
        return None

    # Cloud modes: standard tier follows the canonical stack.
    if tier == "standard":
        canonical = STANDARD_100_EUR_STACK.get(role)
        if canonical and canonical in CATALOGUE_BY_SLUG:
            return CATALOGUE_BY_SLUG[canonical]

    # Hobby tier: role-specific overrides that beat pure-price sorting.
    #
    # log_platform : Grafana Cloud wins over Axiom — same 0-EUR entry
    #   price but bundles logs + metrics + traces in one pane.
    # postgres     : Supabase wins over Neon — same 0-EUR entry price
    #   but ships with pgvector, RLS auth and storage buckets, so a
    #   hobby operator gets three roles worth of infrastructure from
    #   one signup instead of three.
    #
    # All overrides are skipped when the operator asked for
    # `prefer_open_source=True` — they're all managed services.
    if tier == "hobby":
        hobby_overrides: dict[StackRole, str] = {
            "log_platform": "grafana_cloud",
            "postgres":     "supabase",
        }
        override_slug = hobby_overrides.get(role)
        if override_slug and not prefs.prefer_open_source:
            override = CATALOGUE_BY_SLUG.get(override_slug)
            if override and "hobby" in override.tiers:
                return override

    # Free / hobby / scale: pick the cheapest that offers the tier,
    # respecting the open-source and scale-to-zero preferences.
    def _score(s: StackService) -> tuple:
        tier_penalty = 0 if tier in s.tiers else 1
        oss_bonus = 0 if (prefs.prefer_open_source and s.open_source) else 1
        stz_bonus = 0 if (prefs.prefer_scale_to_zero and s.scale_to_zero) else 1
        price = (
            s.price_free_usd if tier == "free" else
            s.price_entry_usd if tier in ("hobby", "standard") else
            s.price_scale_usd
        )
        return (tier_penalty, oss_bonus, stz_bonus, price)

    return sorted(candidates, key=_score)[0]


def _price_for_tier(svc: StackService, tier: BudgetTier) -> float:
    return {
        "free":     svc.price_free_usd,
        "hobby":    svc.price_entry_usd,
        "standard": svc.price_entry_usd,
        "scale":    svc.price_scale_usd,
    }[tier]


def recommend_stack(prefs: StackPreferences) -> StackSelection:
    """Turn preferences into a concrete ``StackSelection``.

    Deterministic + pure so it's trivial to test.
    """
    tier = _tier_from_budget(prefs.monthly_budget_eur)
    picks: dict[StackRole, str] = {}
    total = 0.0

    included_roles: set[StackRole] = set(_CORE_ROLES)
    for role, pref_attr in _OPTIONAL_ROLES.items():
        if getattr(prefs, pref_attr, False):
            included_roles.add(role)

    # Auth is always included — team_size > 1 or governance requires it.
    included_roles.add("auth")
    # Error monitoring + logs are always useful.
    included_roles.add("error_monitoring")
    included_roles.add("log_platform")
    included_roles.add("email_transactional")

    for role in included_roles:
        svc = _pick_for_role(role, prefs, tier)
        if svc is None:
            continue
        picks[role] = svc.slug
        total += _price_for_tier(svc, tier)

    if prefs.deployment_mode == "local":
        rationale = (
            "Local mode: self-hostable services on your own hardware. "
            f"Managed add-ons (GPU, LLM gateway) still count against budget."
        )
    elif tier == "standard":
        rationale = (
            "Standard 100-EUR/month cloud stack: Railway + Vercel + Neon + "
            "Qdrant + Modal + PostHog + Langfuse. Balances DX, cost, and "
            "future scale."
        )
    elif tier == "free":
        rationale = (
            "Free-tier stack: everything on managed free plans. Great to "
            "prototype; expect quota walls around 100-200 monthly users."
        )
    elif tier == "hobby":
        rationale = (
            "Hobby stack: minimal paid tiers, mostly self-hosted or free."
        )
    else:
        rationale = (
            "Scale stack: managed services with headroom for 100+ users; "
            "Postgres + vector DB + GPU inference on paid tiers."
        )

    return StackSelection(
        services=picks,
        estimated_monthly_usd=round(total, 2),
        tier=tier,
        rationale=rationale,
    )


# ---------------------------------------------------------------------------
# Stack config carried through the wizard submission.
# ---------------------------------------------------------------------------


class StackConfig(BaseModel):
    """What ends up in ``nexus.instance.yaml`` under ``spec.stack``."""

    preferences: StackPreferences = Field(default_factory=StackPreferences)
    selection: StackSelection = Field(default_factory=StackSelection)
    overrides: dict[StackRole, str] = Field(
        default_factory=dict,
        description="Manual overrides applied on top of the recommender.",
    )
    host: "HostCapabilities | None" = Field(
        default=None,
        description="Operator's laptop specs — gates local deployment and shapes the handoff.",
    )

    def effective_services(self) -> dict[StackRole, str]:
        """Return selection with overrides applied."""
        merged = dict(self.selection.services)
        merged.update(self.overrides)
        return merged

    @field_validator("overrides")
    @classmethod
    def _valid_overrides(cls, v: dict[StackRole, str]) -> dict[StackRole, str]:
        for role, slug in v.items():
            svc = CATALOGUE_BY_SLUG.get(slug)
            if svc is None:
                raise ValueError(f"unknown service slug: {slug}")
            if svc.role != role:
                raise ValueError(
                    f"service {slug!r} has role {svc.role!r}, not {role!r}"
                )
        return v
