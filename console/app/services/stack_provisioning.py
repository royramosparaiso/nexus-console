"""Handoff playbook fragments for each managed service in the stack.

`stack_provisioning.py` turns a `StackConfig` (produced by the wizard's
Stack step) into extra provider steps + required secrets that are folded
into the main `nexus.handoff.md` playbook.

Every command here uses `${VAR}` placeholders only — real secret values
live in `nexus.secrets.env` (0600, .gitignored) and are resolved at
deploy time. Nothing in this module ever inlines a token, key or
password: that is the contract the whole handoff design depends on.

Provisioning is intentionally shallow: we emit the commands + env vars a
human operator (or a setup-automation agent like Cloud Cowork / OpenClaw)
needs to run once. The runtime code inside Platform then reads the
resulting env vars — never anything from this file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.models.stack import CATALOGUE_BY_SLUG, StackConfig, StackRole


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass
class ServiceHandoff:
    """Playbook fragment for one managed service.

    `steps` — ordered list of `{title, cmd}` dicts, same shape the main
              playbook already consumes.
    `secrets` — env vars the operator must populate in `nexus.secrets.env`
                before running the steps.
    `notes` — free-form Markdown appended to the playbook after the step
              list. Great for "sign up here" links or gotchas.
    """

    slug: str
    role: StackRole
    steps: list[dict] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Per-service builders (standard 100 EUR preset first, then the rest).
# ---------------------------------------------------------------------------


def _railway() -> ServiceHandoff:
    return ServiceHandoff(
        slug="railway",
        role="app_compute",
        secrets=["RAILWAY_API_TOKEN", "RAILWAY_PROJECT_ID"],
        steps=[
            {
                "title": "Authenticate the Railway CLI",
                "cmd": "railway login --token ${RAILWAY_API_TOKEN}",
            },
            {
                "title": "Link the local repo to the Railway project",
                "cmd": "railway link ${RAILWAY_PROJECT_ID}",
            },
            {
                "title": "Push all secrets required by Platform",
                "cmd": (
                    "railway variables set "
                    "PLATFORM_BOOTSTRAP_TOKEN=${PLATFORM_BOOTSTRAP_TOKEN} "
                    "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} "
                    "OPENROUTER_API_KEY=${OPENROUTER_API_KEY}"
                ),
            },
            {
                "title": "Deploy the Platform service",
                "cmd": "railway up --service platform --detach",
            },
        ],
        notes=(
            "Railway auto-detects the Dockerfile in the repo root. Create the "
            "project once from the dashboard (railway.com → New Project → "
            "Empty Project), copy the project id, then this playbook is safe "
            "to re-run for redeploys."
        ),
    )


def _vercel() -> ServiceHandoff:
    return ServiceHandoff(
        slug="vercel",
        role="frontend_hosting",
        secrets=["VERCEL_API_TOKEN", "VERCEL_ORG_ID", "VERCEL_PROJECT_ID"],
        steps=[
            {
                "title": "Link the web workspace to Vercel",
                "cmd": (
                    "cd web && vercel link --yes "
                    "--token ${VERCEL_API_TOKEN} "
                    "--scope ${VERCEL_ORG_ID} "
                    "--project ${VERCEL_PROJECT_ID}"
                ),
            },
            {
                "title": "Push the Platform endpoint as a Vercel env var",
                "cmd": (
                    "vercel env add VITE_PLATFORM_URL production "
                    "--token ${VERCEL_API_TOKEN} <<< ${PLATFORM_PUBLIC_URL}"
                ),
            },
            {
                "title": "Deploy the web bundle to production",
                "cmd": "cd web && vercel --prod --yes --token ${VERCEL_API_TOKEN}",
            },
        ],
    )


def _neon() -> ServiceHandoff:
    return ServiceHandoff(
        slug="neon",
        role="postgres",
        secrets=["NEON_API_KEY", "NEON_PROJECT_ID", "DATABASE_URL"],
        steps=[
            {
                "title": "Create a Postgres branch for this instance (idempotent)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://console.neon.tech/api/v2/projects/${NEON_PROJECT_ID}/branches "
                    "-H 'Authorization: Bearer ${NEON_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"branch\":{\"name\":\"nexus-main\"}}'"
                ),
            },
            {
                "title": "Retrieve the DATABASE_URL and paste it into nexus.secrets.env",
                "cmd": (
                    "curl -fsSL "
                    "https://console.neon.tech/api/v2/projects/${NEON_PROJECT_ID}/connection_uri "
                    "-H 'Authorization: Bearer ${NEON_API_KEY}'"
                ),
            },
            {
                "title": "Enable pgvector extension",
                "cmd": "psql ${DATABASE_URL} -c 'CREATE EXTENSION IF NOT EXISTS vector;'",
            },
        ],
    )


def _neo4j_aura() -> ServiceHandoff:
    return ServiceHandoff(
        slug="neo4j_aura",
        role="graph_db",
        secrets=[
            "NEO4J_AURA_CLIENT_ID",
            "NEO4J_AURA_CLIENT_SECRET",
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
        ],
        steps=[
            {
                "title": "Create an AuraDB Free instance from the dashboard",
                "cmd": (
                    "# Neo4j does not expose full CLI provisioning on Free tier. "
                    "# Visit https://console.neo4j.io, create 'AuraDB Free' with name "
                    "# 'nexus-graph', then paste the connection URI + password into "
                    "# nexus.secrets.env as NEO4J_URI / NEO4J_PASSWORD."
                ),
            },
            {
                "title": "Smoke-test the connection",
                "cmd": (
                    "cypher-shell -a ${NEO4J_URI} -u ${NEO4J_USER} -p ${NEO4J_PASSWORD} "
                    "'RETURN 1 AS ok'"
                ),
            },
        ],
    )


def _qdrant_cloud() -> ServiceHandoff:
    return ServiceHandoff(
        slug="qdrant_cloud",
        role="vector_db",
        secrets=["QDRANT_CLOUD_API_KEY", "QDRANT_CLUSTER_ID", "QDRANT_URL"],
        steps=[
            {
                "title": "Create a free Qdrant cluster (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST https://cloud.qdrant.io/api/v1/clusters "
                    "-H 'Authorization: apikey ${QDRANT_CLOUD_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus-vectors\",\"cloud_provider\":\"gcp\",\"region\":\"europe-west3\"}'"
                ),
            },
            {
                "title": "Copy the cluster URL into nexus.secrets.env as QDRANT_URL",
                "cmd": (
                    "curl -fsSL https://cloud.qdrant.io/api/v1/clusters/${QDRANT_CLUSTER_ID} "
                    "-H 'Authorization: apikey ${QDRANT_CLOUD_API_KEY}'"
                ),
            },
        ],
    )


def _upstash() -> ServiceHandoff:
    return ServiceHandoff(
        slug="upstash",
        role="cache_queue",
        secrets=[
            "UPSTASH_EMAIL",
            "UPSTASH_API_KEY",
            "UPSTASH_REDIS_REST_URL",
            "UPSTASH_REDIS_REST_TOKEN",
            "QSTASH_TOKEN",
        ],
        steps=[
            {
                "title": "Create a Redis database (idempotent)",
                "cmd": (
                    "curl -fsSL -X POST https://api.upstash.com/v2/redis/database "
                    "-u ${UPSTASH_EMAIL}:${UPSTASH_API_KEY} "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus-redis\",\"region\":\"eu-west-1\",\"tls\":true}'"
                ),
            },
            {
                "title": "Paste REST URL + token into nexus.secrets.env",
                "cmd": (
                    "# Upstash returns rest_url + rest_token in the JSON response. "
                    "# Copy them into UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN. "
                    "# QSTASH_TOKEN is separate; grab it from console.upstash.com > QStash."
                ),
            },
        ],
    )


def _modal() -> ServiceHandoff:
    return ServiceHandoff(
        slug="modal",
        role="gpu_serverless",
        secrets=["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"],
        steps=[
            {
                "title": "Configure the Modal CLI",
                "cmd": (
                    "modal token set "
                    "--token-id ${MODAL_TOKEN_ID} "
                    "--token-secret ${MODAL_TOKEN_SECRET}"
                ),
            },
            {
                "title": "Deploy the Kokoro voice function",
                "cmd": "modal deploy ironbat_jarvis/modal_kokoro.py",
            },
            {
                "title": "Register the invocation URL as KOKORO_URL",
                "cmd": (
                    "# `modal deploy` prints an https URL. Paste it into "
                    "# nexus.secrets.env as KOKORO_URL — Platform reads that at boot."
                ),
            },
        ],
    )


def _openrouter() -> ServiceHandoff:
    return ServiceHandoff(
        slug="openrouter",
        role="llm_gateway",
        secrets=["OPENROUTER_API_KEY"],
        steps=[
            {
                "title": "Create an OpenRouter API key",
                "cmd": (
                    "# Visit https://openrouter.ai/settings/keys, create a key named "
                    "# 'nexus', paste into nexus.secrets.env as OPENROUTER_API_KEY."
                ),
            },
            {
                "title": "Verify with a routing probe",
                "cmd": (
                    "curl -fsSL https://openrouter.ai/api/v1/auth/key "
                    "-H 'Authorization: Bearer ${OPENROUTER_API_KEY}'"
                ),
            },
        ],
    )


def _cloudflare_r2() -> ServiceHandoff:
    return ServiceHandoff(
        slug="cloudflare_r2",
        role="object_storage",
        secrets=[
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_API_TOKEN",
            "R2_ACCESS_KEY_ID",
            "R2_SECRET_ACCESS_KEY",
            "R2_BUCKET",
        ],
        steps=[
            {
                "title": "Create the R2 bucket (idempotent)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/r2/buckets "
                    "-H 'Authorization: Bearer ${CLOUDFLARE_API_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${R2_BUCKET}\"}'"
                ),
            },
            {
                "title": "Mint an R2 access-key pair",
                "cmd": (
                    "# Cloudflare dashboard → R2 → Manage R2 API Tokens → Create. "
                    "# Paste the access key + secret into nexus.secrets.env as "
                    "# R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY."
                ),
            },
        ],
    )


def _clerk() -> ServiceHandoff:
    return ServiceHandoff(
        slug="clerk",
        role="auth",
        secrets=["CLERK_SECRET_KEY", "CLERK_PUBLISHABLE_KEY", "CLERK_JWKS_URL"],
        steps=[
            {
                "title": "Create a Clerk application from the dashboard",
                "cmd": (
                    "# https://dashboard.clerk.com → Create Application → 'nexus'. "
                    "# Copy publishable + secret keys into nexus.secrets.env."
                ),
            },
            {
                "title": "Copy the JWKS endpoint",
                "cmd": (
                    "# Clerk dashboard → API Keys → Advanced → JWKS endpoint. "
                    "# Paste into CLERK_JWKS_URL — Platform verifies JWTs against it."
                ),
            },
        ],
    )


def _cloudflare_dns() -> ServiceHandoff:
    return ServiceHandoff(
        slug="cloudflare",
        role="dns_cdn",
        secrets=[
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_API_TOKEN",
            "CLOUDFLARE_ZONE_ID",
            "NEXUS_DOMAIN",
        ],
        steps=[
            {
                "title": "Point the apex/subdomain at the Platform endpoint",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/dns_records "
                    "-H 'Authorization: Bearer ${CLOUDFLARE_API_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"type\":\"CNAME\",\"name\":\"${NEXUS_DOMAIN}\",\"content\":\"${PLATFORM_PUBLIC_HOST}\",\"proxied\":true}'"
                ),
            },
        ],
    )


def _sentry() -> ServiceHandoff:
    return ServiceHandoff(
        slug="sentry",
        role="error_monitoring",
        secrets=[
            "SENTRY_AUTH_TOKEN",
            "SENTRY_ORG",
            "SENTRY_PROJECT",
            "SENTRY_DSN",
        ],
        steps=[
            {
                "title": "Create the Sentry project (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://sentry.io/api/0/teams/${SENTRY_ORG}/nexus/projects/ "
                    "-H 'Authorization: Bearer ${SENTRY_AUTH_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${SENTRY_PROJECT}\",\"platform\":\"python\"}'"
                ),
            },
            {
                "title": "Fetch the DSN and paste it into nexus.secrets.env",
                "cmd": (
                    "curl -fsSL "
                    "https://sentry.io/api/0/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/keys/ "
                    "-H 'Authorization: Bearer ${SENTRY_AUTH_TOKEN}'"
                ),
            },
        ],
    )


def _axiom() -> ServiceHandoff:
    return ServiceHandoff(
        slug="axiom",
        role="log_platform",
        secrets=["AXIOM_API_TOKEN", "AXIOM_ORG_ID", "AXIOM_DATASET"],
        steps=[
            {
                "title": "Create the Axiom dataset (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST https://api.axiom.co/v1/datasets "
                    "-H 'Authorization: Bearer ${AXIOM_API_TOKEN}' "
                    "-H 'X-Axiom-Org-Id: ${AXIOM_ORG_ID}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${AXIOM_DATASET}\",\"description\":\"Nexus platform logs\"}'"
                ),
            },
        ],
    )


def _posthog() -> ServiceHandoff:
    return ServiceHandoff(
        slug="posthog",
        role="product_analytics",
        secrets=[
            "POSTHOG_PERSONAL_API_KEY",
            "POSTHOG_PROJECT_API_KEY",
            "POSTHOG_HOST",
        ],
        steps=[
            {
                "title": "Create the PostHog project (idempotent — 400 if name taken)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://${POSTHOG_HOST}/api/organizations/@current/projects/ "
                    "-H 'Authorization: Bearer ${POSTHOG_PERSONAL_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus\"}'"
                ),
            },
            {
                "title": "Copy the project's public API key into nexus.secrets.env",
                "cmd": (
                    "curl -fsSL "
                    "https://${POSTHOG_HOST}/api/projects/@current/ "
                    "-H 'Authorization: Bearer ${POSTHOG_PERSONAL_API_KEY}'"
                ),
            },
        ],
    )


def _langfuse() -> ServiceHandoff:
    return ServiceHandoff(
        slug="langfuse",
        role="llm_observability",
        secrets=[
            "LANGFUSE_HOST",
            "LANGFUSE_PUBLIC_KEY",
            "LANGFUSE_SECRET_KEY",
        ],
        steps=[
            {
                "title": "Create a Langfuse project from the dashboard",
                "cmd": (
                    "# https://cloud.langfuse.com → New Project → 'nexus'. "
                    "# Copy the public + secret keys into nexus.secrets.env. "
                    "# LANGFUSE_HOST defaults to https://cloud.langfuse.com."
                ),
            },
        ],
    )


def _resend() -> ServiceHandoff:
    return ServiceHandoff(
        slug="resend",
        role="email_transactional",
        secrets=["RESEND_API_KEY", "RESEND_FROM_ADDRESS"],
        steps=[
            {
                "title": "Create a Resend API key from the dashboard",
                "cmd": (
                    "# https://resend.com/api-keys → Create → 'nexus'. "
                    "# Paste into nexus.secrets.env as RESEND_API_KEY."
                ),
            },
            {
                "title": "Verify the sender domain",
                "cmd": (
                    "curl -fsSL -X POST https://api.resend.com/domains "
                    "-H 'Authorization: Bearer ${RESEND_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${NEXUS_DOMAIN}\"}'"
                ),
            },
        ],
    )


def _trigger_dev() -> ServiceHandoff:
    return ServiceHandoff(
        slug="trigger_dev",
        role="background_jobs",
        secrets=["TRIGGER_API_KEY", "TRIGGER_PROJECT_REF"],
        steps=[
            {
                "title": "Log in to the Trigger.dev CLI",
                "cmd": "npx trigger.dev@latest login --token ${TRIGGER_API_KEY}",
            },
            {
                "title": "Deploy the jobs project",
                "cmd": (
                    "cd trigger && npx trigger.dev@latest deploy "
                    "--project-ref ${TRIGGER_PROJECT_REF}"
                ),
            },
        ],
    )


def _github_actions() -> ServiceHandoff:
    return ServiceHandoff(
        slug="github_actions",
        role="ci_cd",
        secrets=["GITHUB_TOKEN"],
        steps=[
            {
                "title": "GitHub Actions is auto-provisioned by pushing to the repo",
                "cmd": (
                    "# No extra provisioning needed — the workflows live in "
                    "# .github/workflows/. Secrets used at CI time (RAILWAY_API_TOKEN, "
                    "# VERCEL_API_TOKEN, etc.) must be added under "
                    "# Settings → Secrets → Actions in the GitHub UI."
                ),
            },
        ],
    )


# ---------------------------------------------------------------------------
# Registry.
# ---------------------------------------------------------------------------


_BUILDERS: dict[str, Callable[[], ServiceHandoff]] = {
    # Standard 100 EUR preset.
    "railway": _railway,
    "vercel": _vercel,
    "neon": _neon,
    "neo4j_aura": _neo4j_aura,
    "qdrant_cloud": _qdrant_cloud,
    "upstash": _upstash,
    "modal": _modal,
    "openrouter": _openrouter,
    "cloudflare_r2": _cloudflare_r2,
    "clerk": _clerk,
    "cloudflare": _cloudflare_dns,
    "sentry": _sentry,
    "axiom": _axiom,
    "posthog": _posthog,
    "langfuse": _langfuse,
    "resend": _resend,
    "trigger_dev": _trigger_dev,
    "github_actions": _github_actions,
}


def handoff_for(slug: str) -> ServiceHandoff | None:
    """Return the handoff fragment for one service, or None if unknown."""
    builder = _BUILDERS.get(slug)
    return builder() if builder else None


def stack_handoffs(stack: StackConfig) -> list[ServiceHandoff]:
    """Ordered list of handoffs for the effective services in the stack.

    Ordering: infrastructure roles first (compute → DB → cache), then
    observability and jobs. This is the order an operator would run them
    top-to-bottom in the playbook.
    """
    role_order: list[StackRole] = [
        "app_compute", "frontend_hosting",
        "postgres", "graph_db", "vector_db", "cache_queue",
        "object_storage",
        "llm_gateway", "gpu_serverless",
        "auth", "dns_cdn",
        "error_monitoring", "log_platform",
        "product_analytics", "llm_observability",
        "email_transactional", "background_jobs",
        "ci_cd",
    ]
    services = stack.effective_services()
    out: list[ServiceHandoff] = []
    for role in role_order:
        slug = services.get(role)
        if not slug:
            continue
        fragment = handoff_for(slug)
        if fragment is None:
            # Unknown to the playbook (e.g. self-hosted only) — skip
            # silently; the YAML still records the pick.
            continue
        out.append(fragment)
    return out


def merge_into_playbook_inputs(playbook_inputs, stack: StackConfig | None) -> None:
    """In-place extend a `PlaybookInputs` with stack-driven steps + secrets.

    Called from `wizard.py` right before `write_playbook(...)`. If `stack`
    is None we do nothing — legacy flows keep working.
    """
    if stack is None:
        return
    handoffs = stack_handoffs(stack)
    if not handoffs:
        return

    # Merge secrets (order-preserving dedup).
    seen = set(playbook_inputs.required_secrets)
    for h in handoffs:
        for s in h.secrets:
            if s not in seen:
                playbook_inputs.required_secrets.append(s)
                seen.add(s)

    # Append a section header + each service's steps.
    playbook_inputs.provider_steps.append({
        "title": "── Stack services (from wizard Step 7) ──",
        "cmd": "# The steps below configure the managed services this "
               "instance picked. Each one is idempotent.",
    })
    for h in handoffs:
        svc = CATALOGUE_BY_SLUG.get(h.slug)
        header_title = f"[{h.role}] {svc.name if svc else h.slug}"
        playbook_inputs.provider_steps.append({
            "title": header_title,
            "cmd": f"# {svc.homepage if svc else h.slug} — {svc.notes if svc and svc.notes else 'managed service'}",
        })
        for step in h.steps:
            playbook_inputs.provider_steps.append({
                "title": f"  ↳ {step['title']}",
                "cmd": step["cmd"],
            })
