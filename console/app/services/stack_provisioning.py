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
# Alternatives — free-tier and lower-cost swaps for the standard preset.
# Only services with a real free tier + a scriptable/API-driven onboarding
# get a builder. Self-host-only picks (loki_self_host, kuzu_embedded,
# local_postgres, local_redis, litellm_proxy, fly_postgres) are documented
# in the catalogue but do not emit playbook steps — the operator runs them
# inside their own compute.
# ---------------------------------------------------------------------------


# ---- app_compute alternatives ----

def _fly() -> ServiceHandoff:
    return ServiceHandoff(
        slug="fly",
        role="app_compute",
        secrets=["FLY_API_TOKEN", "FLY_APP_NAME"],
        steps=[
            {
                "title": "Authenticate flyctl",
                "cmd": "fly auth token ${FLY_API_TOKEN}",
            },
            {
                "title": "Launch the Platform app (idempotent — skip if fly.toml already deployed)",
                "cmd": "fly launch --name ${FLY_APP_NAME} --copy-config --no-deploy",
            },
            {
                "title": "Set Platform secrets from nexus.secrets.env",
                "cmd": (
                    "fly secrets set --app ${FLY_APP_NAME} "
                    "PLATFORM_BOOTSTRAP_TOKEN=${PLATFORM_BOOTSTRAP_TOKEN} "
                    "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
                ),
            },
            {
                "title": "Deploy",
                "cmd": "fly deploy --app ${FLY_APP_NAME}",
            },
        ],
        notes=(
            "Same Fly.io flow as the built-in cloud modality — use this when "
            "you want Fly as the compute layer but keep the rest of the "
            "stack managed elsewhere."
        ),
    )


def _render() -> ServiceHandoff:
    return ServiceHandoff(
        slug="render",
        role="app_compute",
        secrets=["RENDER_API_KEY", "RENDER_OWNER_ID", "RENDER_SERVICE_ID", "GITHUB_ORG"],
        steps=[
            {
                "title": "Create a web service from the repo (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST https://api.render.com/v1/services "
                    "-H 'Authorization: Bearer ${RENDER_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"type\":\"web_service\",\"name\":\"nexus-platform\",\"ownerId\":\"${RENDER_OWNER_ID}\",\"repo\":\"https://github.com/${GITHUB_ORG}/nexus-platform\",\"branch\":\"main\",\"serviceDetails\":{\"env\":\"docker\",\"plan\":\"starter\"}}'"
                ),
            },
            {
                "title": "List services to grab the service id (paste into RENDER_SERVICE_ID)",
                "cmd": (
                    "curl -fsSL https://api.render.com/v1/services "
                    "-H 'Authorization: Bearer ${RENDER_API_KEY}'"
                ),
            },
            {
                "title": "Push env vars",
                "cmd": (
                    "curl -fsSL -X PUT "
                    "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/env-vars "
                    "-H 'Authorization: Bearer ${RENDER_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '[{\"key\":\"PLATFORM_BOOTSTRAP_TOKEN\",\"value\":\"${PLATFORM_BOOTSTRAP_TOKEN}\"}]'"
                ),
            },
        ],
    )


# ---- frontend_hosting alternatives ----

def _cloudflare_pages() -> ServiceHandoff:
    return ServiceHandoff(
        slug="cloudflare_pages",
        role="frontend_hosting",
        secrets=[
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_API_TOKEN",
            "CF_PAGES_PROJECT",
        ],
        steps=[
            {
                "title": "Create the Pages project (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects "
                    "-H 'Authorization: Bearer ${CLOUDFLARE_API_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${CF_PAGES_PROJECT}\",\"production_branch\":\"main\"}'"
                ),
            },
            {
                "title": "Build the frontend and deploy with wrangler",
                "cmd": (
                    "cd web && npm run build && "
                    "CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN} "
                    "CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID} "
                    "npx wrangler pages deploy dist --project-name ${CF_PAGES_PROJECT}"
                ),
            },
        ],
    )


def _netlify() -> ServiceHandoff:
    return ServiceHandoff(
        slug="netlify",
        role="frontend_hosting",
        secrets=["NETLIFY_AUTH_TOKEN", "NETLIFY_SITE_ID"],
        steps=[
            {
                "title": "Log in and link the site",
                "cmd": (
                    "cd web && netlify login --auth-token ${NETLIFY_AUTH_TOKEN} && "
                    "netlify link --id ${NETLIFY_SITE_ID}"
                ),
            },
            {
                "title": "Build + deploy to production",
                "cmd": "cd web && npm run build && netlify deploy --prod --dir dist",
            },
        ],
    )


# ---- postgres alternatives ----

def _supabase() -> ServiceHandoff:
    return ServiceHandoff(
        slug="supabase",
        role="postgres",
        secrets=[
            "SUPABASE_ACCESS_TOKEN",
            "SUPABASE_ORG_ID",
            "SUPABASE_PROJECT_REF",
            "SUPABASE_DB_PASSWORD",
            "DATABASE_URL",
        ],
        steps=[
            {
                "title": "Create the Supabase project (idempotent — 409 if the ref exists)",
                "cmd": (
                    "curl -fsSL -X POST https://api.supabase.com/v1/projects "
                    "-H 'Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus\",\"organization_id\":\"${SUPABASE_ORG_ID}\",\"region\":\"eu-west-1\",\"db_pass\":\"${SUPABASE_DB_PASSWORD}\",\"plan\":\"free\"}'"
                ),
            },
            {
                "title": "Fetch the connection string (paste into DATABASE_URL)",
                "cmd": (
                    "curl -fsSL "
                    "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/database "
                    "-H 'Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}'"
                ),
            },
            {
                "title": "Enable pgvector",
                "cmd": "psql ${DATABASE_URL} -c 'CREATE EXTENSION IF NOT EXISTS vector;'",
            },
        ],
        notes=(
            "Supabase free tier: 500 MB Postgres + 1 GB storage + pgvector "
            "built in. Drop-in replacement for Neon when you also want "
            "row-level auth or storage in the same project."
        ),
    )


# ---- graph_db alternatives ----

def _memgraph_cloud() -> ServiceHandoff:
    return ServiceHandoff(
        slug="memgraph_cloud",
        role="graph_db",
        secrets=[
            "MEMGRAPH_HOST",
            "MEMGRAPH_PORT",
            "MEMGRAPH_USER",
            "MEMGRAPH_PASSWORD",
        ],
        steps=[
            {
                "title": "Create a Memgraph Cloud project from the dashboard",
                "cmd": (
                    "# https://cloud.memgraph.com → New Project → 'nexus-graph'. "
                    "# Copy host + port + credentials into nexus.secrets.env."
                ),
            },
            {
                "title": "Smoke-test with the Bolt endpoint",
                "cmd": (
                    "mgconsole --host ${MEMGRAPH_HOST} --port ${MEMGRAPH_PORT} "
                    "--username ${MEMGRAPH_USER} --password ${MEMGRAPH_PASSWORD} "
                    "--execute 'RETURN 1 AS ok;'"
                ),
            },
        ],
        notes=(
            "Bolt-compatible with Neo4j drivers — change the URI and the "
            "application code keeps working. Faster on write-heavy graphs."
        ),
    )


# ---- vector_db alternatives ----

def _turbopuffer() -> ServiceHandoff:
    return ServiceHandoff(
        slug="turbopuffer",
        role="vector_db",
        secrets=["TURBOPUFFER_API_KEY", "TURBOPUFFER_REGION"],
        steps=[
            {
                "title": "Grab an API key from the dashboard",
                "cmd": (
                    "# https://turbopuffer.com/dashboard → New API Key → paste into "
                    "# nexus.secrets.env as TURBOPUFFER_API_KEY. "
                    "# TURBOPUFFER_REGION defaults to gcp-us-east4."
                ),
            },
            {
                "title": "Probe the API",
                "cmd": (
                    "curl -fsSL https://api.turbopuffer.com/v1/namespaces "
                    "-H 'Authorization: Bearer ${TURBOPUFFER_API_KEY}'"
                ),
            },
        ],
        notes="Object-storage-backed vectors — pennies per million at rest.",
    )


def _pinecone() -> ServiceHandoff:
    return ServiceHandoff(
        slug="pinecone",
        role="vector_db",
        secrets=["PINECONE_API_KEY", "PINECONE_INDEX", "PINECONE_HOST"],
        steps=[
            {
                "title": "Create the serverless index (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST https://api.pinecone.io/indexes "
                    "-H 'Api-Key: ${PINECONE_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${PINECONE_INDEX}\",\"dimension\":1536,\"metric\":\"cosine\",\"spec\":{\"serverless\":{\"cloud\":\"aws\",\"region\":\"us-east-1\"}}}'"
                ),
            },
            {
                "title": "Fetch the index host (paste into PINECONE_HOST)",
                "cmd": (
                    "curl -fsSL https://api.pinecone.io/indexes/${PINECONE_INDEX} "
                    "-H 'Api-Key: ${PINECONE_API_KEY}'"
                ),
            },
        ],
    )


def _pgvector() -> ServiceHandoff:
    return ServiceHandoff(
        slug="pgvector",
        role="vector_db",
        secrets=["DATABASE_URL"],
        steps=[
            {
                "title": "Enable the pgvector extension in the app database",
                "cmd": "psql ${DATABASE_URL} -c 'CREATE EXTENSION IF NOT EXISTS vector;'",
            },
            {
                "title": "Create the embeddings table (safe to re-run)",
                "cmd": (
                    "psql ${DATABASE_URL} -c \"CREATE TABLE IF NOT EXISTS "
                    "nexus_embeddings (id UUID PRIMARY KEY, embedding vector(1536), "
                    "metadata JSONB);\""
                ),
            },
        ],
        notes=(
            "Zero-extra-cost: reuses the Postgres you already picked. Fine "
            "until ~1M vectors; graduate to Qdrant Cloud or Turbopuffer past that."
        ),
    )


# ---- cache_queue alternatives ----

def _redis_cloud() -> ServiceHandoff:
    return ServiceHandoff(
        slug="redis_cloud",
        role="cache_queue",
        secrets=[
            "REDIS_CLOUD_API_KEY",
            "REDIS_CLOUD_ACCOUNT_KEY",
            "REDIS_URL",
        ],
        steps=[
            {
                "title": "Create a free Redis Cloud subscription",
                "cmd": (
                    "curl -fsSL -X POST https://api.redislabs.com/v1/subscriptions "
                    "-H 'x-api-key: ${REDIS_CLOUD_ACCOUNT_KEY}' "
                    "-H 'x-api-secret-key: ${REDIS_CLOUD_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus-redis\",\"paymentMethod\":\"credit-card\",\"cloudProviders\":[{\"provider\":\"AWS\",\"regions\":[{\"region\":\"eu-west-1\",\"networking\":{\"deploymentCIDR\":\"10.0.0.0/24\"}}]}],\"databases\":[{\"name\":\"nexus\",\"memoryLimitInGb\":0.03}]}'"
                ),
            },
            {
                "title": "Copy the private endpoint into REDIS_URL",
                "cmd": (
                    "# The response contains 'publicEndpoint' — paste as "
                    "# REDIS_URL=redis://default:PASSWORD@host:port in nexus.secrets.env."
                ),
            },
        ],
    )


# ---- gpu_serverless alternatives ----

def _runpod_serverless() -> ServiceHandoff:
    return ServiceHandoff(
        slug="runpod_serverless",
        role="gpu_serverless",
        secrets=["RUNPOD_API_KEY", "RUNPOD_ENDPOINT_ID"],
        steps=[
            {
                "title": "Create a serverless endpoint from the Kokoro template",
                "cmd": (
                    "curl -fsSL -X POST https://api.runpod.io/graphql "
                    "-H 'Authorization: Bearer ${RUNPOD_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"query\":\"mutation { saveEndpoint(input: {name: \\\"nexus-kokoro\\\", templateId: \\\"runpod-kokoro\\\", gpuIds: \\\"NVIDIA GeForce RTX 4090\\\"}) { id } }\"}'"
                ),
            },
            {
                "title": "Copy the endpoint URL into KOKORO_URL",
                "cmd": (
                    "# RunPod prints https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/run — "
                    "# paste as KOKORO_URL in nexus.secrets.env."
                ),
            },
        ],
    )


def _replicate() -> ServiceHandoff:
    return ServiceHandoff(
        slug="replicate",
        role="gpu_serverless",
        secrets=["REPLICATE_API_TOKEN"],
        steps=[
            {
                "title": "Verify the API token",
                "cmd": (
                    "curl -fsSL https://api.replicate.com/v1/account "
                    "-H 'Authorization: Token ${REPLICATE_API_TOKEN}'"
                ),
            },
            {
                "title": "Point Platform at Replicate as the TTS backend",
                "cmd": (
                    "# Set VOICE_BACKEND=replicate and VOICE_MODEL=<owner/model:version> "
                    "# in nexus.secrets.env — Platform reads them at boot."
                ),
            },
        ],
        notes=(
            "Pay-per-second inference on hosted models. Cheapest option when "
            "traffic is bursty and you don't want to keep a container warm."
        ),
    )


def _fly_gpu() -> ServiceHandoff:
    return ServiceHandoff(
        slug="fly_gpu",
        role="gpu_serverless",
        secrets=["FLY_API_TOKEN", "FLY_GPU_APP_NAME"],
        steps=[
            {
                "title": "Authenticate flyctl",
                "cmd": "fly auth token ${FLY_API_TOKEN}",
            },
            {
                "title": "Launch a GPU machine for Kokoro",
                "cmd": (
                    "fly launch --name ${FLY_GPU_APP_NAME} "
                    "--image ghcr.io/remsky/kokoro-fastapi-gpu:latest "
                    "--vm-gpu-kind a10 --no-deploy --copy-config"
                ),
            },
            {
                "title": "Deploy and paste the URL into KOKORO_URL",
                "cmd": "fly deploy --app ${FLY_GPU_APP_NAME}",
            },
        ],
    )


# ---- object_storage alternatives ----

def _backblaze_b2() -> ServiceHandoff:
    return ServiceHandoff(
        slug="backblaze_b2",
        role="object_storage",
        secrets=[
            "B2_APPLICATION_KEY_ID",
            "B2_APPLICATION_KEY",
            "B2_BUCKET",
            "B2_ENDPOINT",
        ],
        steps=[
            {
                "title": "Authorise the B2 CLI",
                "cmd": (
                    "b2 authorize-account ${B2_APPLICATION_KEY_ID} ${B2_APPLICATION_KEY}"
                ),
            },
            {
                "title": "Create the bucket (idempotent — exits 1 if it exists, which is fine)",
                "cmd": "b2 create-bucket ${B2_BUCKET} allPrivate || true",
            },
            {
                "title": "Copy the S3-compatible endpoint into B2_ENDPOINT",
                "cmd": "b2 get-account-info | grep s3endpoint",
            },
        ],
        notes="S3-compatible; 10 GB free forever. Egress cheaper than S3.",
    )


def _aws_s3() -> ServiceHandoff:
    return ServiceHandoff(
        slug="aws_s3",
        role="object_storage",
        secrets=[
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
            "S3_BUCKET",
        ],
        steps=[
            {
                "title": "Create the S3 bucket (idempotent — BucketAlreadyOwnedByYou is fine)",
                "cmd": (
                    "aws s3api create-bucket "
                    "--bucket ${S3_BUCKET} --region ${AWS_REGION} "
                    "--create-bucket-configuration LocationConstraint=${AWS_REGION}"
                ),
            },
            {
                "title": "Block public access",
                "cmd": (
                    "aws s3api put-public-access-block "
                    "--bucket ${S3_BUCKET} "
                    "--public-access-block-configuration "
                    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
                ),
            },
        ],
    )


# ---- auth alternatives ----

def _workos() -> ServiceHandoff:
    return ServiceHandoff(
        slug="workos",
        role="auth",
        secrets=["WORKOS_API_KEY", "WORKOS_CLIENT_ID"],
        steps=[
            {
                "title": "Grab the API key + client id from the WorkOS dashboard",
                "cmd": (
                    "# https://dashboard.workos.com → API Keys. Paste both into "
                    "# nexus.secrets.env. Turn on SSO + Directory Sync connectors "
                    "# per customer from the same dashboard."
                ),
            },
            {
                "title": "Verify the key with the API",
                "cmd": (
                    "curl -fsSL https://api.workos.com/user_management/users "
                    "-H 'Authorization: Bearer ${WORKOS_API_KEY}'"
                ),
            },
        ],
        notes="Best pick when you need SSO/SAML for enterprise customers.",
    )


def _better_auth() -> ServiceHandoff:
    return ServiceHandoff(
        slug="better_auth",
        role="auth",
        secrets=["BETTER_AUTH_SECRET", "BETTER_AUTH_URL"],
        steps=[
            {
                "title": "Generate a signing secret",
                "cmd": (
                    "# Run once locally: `openssl rand -base64 32` and paste the "
                    "# output into nexus.secrets.env as BETTER_AUTH_SECRET. "
                    "# BETTER_AUTH_URL is the public Platform URL."
                ),
            },
            {
                "title": "Run migrations against DATABASE_URL",
                "cmd": "npx @better-auth/cli migrate --database ${DATABASE_URL}",
            },
        ],
        notes=(
            "Self-hosted — no external vendor. Auth data lives inside the "
            "Platform Postgres. Zero recurring cost."
        ),
    )


# ---- error_monitoring alternatives ----

def _glitchtip() -> ServiceHandoff:
    return ServiceHandoff(
        slug="glitchtip",
        role="error_monitoring",
        secrets=["GLITCHTIP_HOST", "GLITCHTIP_DSN", "GLITCHTIP_AUTH_TOKEN"],
        steps=[
            {
                "title": "Create the GlitchTip project (managed or self-hosted — same API as Sentry)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "https://${GLITCHTIP_HOST}/api/0/teams/nexus/nexus/projects/ "
                    "-H 'Authorization: Bearer ${GLITCHTIP_AUTH_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus-platform\",\"platform\":\"python\"}'"
                ),
            },
            {
                "title": "Fetch the DSN and paste it into GLITCHTIP_DSN",
                "cmd": (
                    "curl -fsSL "
                    "https://${GLITCHTIP_HOST}/api/0/projects/nexus/nexus-platform/keys/ "
                    "-H 'Authorization: Bearer ${GLITCHTIP_AUTH_TOKEN}'"
                ),
            },
        ],
        notes=(
            "Sentry-compatible SDK — flip SENTRY_DSN to the GlitchTip DSN and "
            "the application code is unchanged."
        ),
    )


# ---- log_platform alternatives ----

def _better_stack() -> ServiceHandoff:
    return ServiceHandoff(
        slug="better_stack",
        role="log_platform",
        secrets=[
            "BETTERSTACK_TEAM_TOKEN",
            "BETTERSTACK_SOURCE_TOKEN",
            "BETTERSTACK_INGEST_HOST",
        ],
        steps=[
            {
                "title": "Create the log source (idempotent — 409 if exists)",
                "cmd": (
                    "curl -fsSL -X POST https://logs.betterstack.com/api/v1/sources "
                    "-H 'Authorization: Bearer ${BETTERSTACK_TEAM_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus-platform\",\"platform\":\"vector\"}'"
                ),
            },
            {
                "title": "Copy the ingest host + source token into nexus.secrets.env",
                "cmd": (
                    "curl -fsSL https://logs.betterstack.com/api/v1/sources "
                    "-H 'Authorization: Bearer ${BETTERSTACK_TEAM_TOKEN}'"
                ),
            },
        ],
    )


def _grafana_cloud() -> ServiceHandoff:
    return ServiceHandoff(
        slug="grafana_cloud",
        role="log_platform",
        secrets=[
            "GRAFANA_CLOUD_STACK_ID",
            "GRAFANA_CLOUD_API_KEY",
            "GRAFANA_LOKI_URL",
            "GRAFANA_LOKI_USER",
            "GRAFANA_PROM_URL",
            "GRAFANA_PROM_USER",
            "GRAFANA_TEMPO_URL",
        ],
        steps=[
            {
                "title": "Create a Grafana Cloud stack (skip if you already have one)",
                "cmd": (
                    "curl -fsSL -X POST https://grafana.com/api/instances "
                    "-H 'Authorization: Bearer ${GRAFANA_CLOUD_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"nexus\",\"slug\":\"nexus\",\"region\":\"eu\"}'"
                ),
            },
            {
                "title": "Fetch the Loki / Prometheus / Tempo endpoints",
                "cmd": (
                    "curl -fsSL https://grafana.com/api/instances/${GRAFANA_CLOUD_STACK_ID} "
                    "-H 'Authorization: Bearer ${GRAFANA_CLOUD_API_KEY}'"
                ),
            },
            {
                "title": "Push logs via Vector or Promtail (see notes)",
                "cmd": (
                    "# Configure the Platform's log shipper with the Loki URL "
                    "# and basic-auth user — both come from the response above."
                ),
            },
        ],
        notes=(
            "Free tier bundles 50 GB logs + 10k metrics series + 50 GB traces. "
            "Better than Axiom if you also want Prometheus metrics + Tempo "
            "traces in the same pane."
        ),
    )


# ---- product_analytics alternatives ----

def _plausible() -> ServiceHandoff:
    return ServiceHandoff(
        slug="plausible",
        role="product_analytics",
        secrets=["PLAUSIBLE_API_KEY", "PLAUSIBLE_SITE_ID"],
        steps=[
            {
                "title": "Create the site (idempotent — 409 if the domain exists)",
                "cmd": (
                    "curl -fsSL -X POST https://plausible.io/api/v1/sites "
                    "-H 'Authorization: Bearer ${PLAUSIBLE_API_KEY}' "
                    "-H 'Content-Type: application/x-www-form-urlencoded' "
                    "-d 'domain=${PLAUSIBLE_SITE_ID}&timezone=Europe/Madrid'"
                ),
            },
            {
                "title": "Verify with the health endpoint",
                "cmd": (
                    "curl -fsSL https://plausible.io/api/v1/sites/${PLAUSIBLE_SITE_ID} "
                    "-H 'Authorization: Bearer ${PLAUSIBLE_API_KEY}'"
                ),
            },
        ],
        notes=(
            "Cookieless, GDPR-friendly, single script tag. Drop-in when you "
            "don't need PostHog's session replay or feature flags."
        ),
    )


# ---- llm_observability alternatives ----

def _langsmith() -> ServiceHandoff:
    return ServiceHandoff(
        slug="langsmith",
        role="llm_observability",
        secrets=["LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT"],
        steps=[
            {
                "title": "Create an API key from the LangSmith dashboard",
                "cmd": (
                    "# https://smith.langchain.com → Settings → API Keys. Paste into "
                    "# nexus.secrets.env. LANGSMITH_ENDPOINT is "
                    "# https://api.smith.langchain.com by default."
                ),
            },
            {
                "title": "Create the project on first trace (idempotent)",
                "cmd": (
                    "curl -fsSL -X POST "
                    "${LANGSMITH_ENDPOINT}/api/v1/sessions "
                    "-H 'x-api-key: ${LANGSMITH_API_KEY}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"name\":\"${LANGSMITH_PROJECT}\"}'"
                ),
            },
        ],
    )


# ---- email_transactional alternatives ----

def _postmark() -> ServiceHandoff:
    return ServiceHandoff(
        slug="postmark",
        role="email_transactional",
        secrets=[
            "POSTMARK_ACCOUNT_TOKEN",
            "POSTMARK_SERVER_TOKEN",
            "POSTMARK_FROM_ADDRESS",
        ],
        steps=[
            {
                "title": "Create a transactional server (idempotent — 409 if the name exists)",
                "cmd": (
                    "curl -fsSL -X POST https://api.postmarkapp.com/servers "
                    "-H 'X-Postmark-Account-Token: ${POSTMARK_ACCOUNT_TOKEN}' "
                    "-H 'Content-Type: application/json' "
                    "-d '{\"Name\":\"nexus\",\"Color\":\"Blue\"}'"
                ),
            },
            {
                "title": "Copy the server token into POSTMARK_SERVER_TOKEN",
                "cmd": (
                    "curl -fsSL https://api.postmarkapp.com/servers "
                    "-H 'X-Postmark-Account-Token: ${POSTMARK_ACCOUNT_TOKEN}'"
                ),
            },
        ],
    )


# ---- background_jobs alternatives ----

def _inngest() -> ServiceHandoff:
    return ServiceHandoff(
        slug="inngest",
        role="background_jobs",
        secrets=[
            "INNGEST_EVENT_KEY",
            "INNGEST_SIGNING_KEY",
            "INNGEST_APP_ID",
        ],
        steps=[
            {
                "title": "Create the Inngest app from the dashboard",
                "cmd": (
                    "# https://app.inngest.com → New App. Copy the event key + "
                    "# signing key into nexus.secrets.env."
                ),
            },
            {
                "title": "Register the served endpoint with Inngest",
                "cmd": (
                    "curl -fsSL -X PUT ${PLATFORM_PUBLIC_URL}/api/inngest "
                    "-H 'Content-Type: application/json'"
                ),
            },
        ],
        notes=(
            "Serverless-native background jobs with automatic retries + "
            "replay. Free tier is generous — 25k steps/month."
        ),
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
    # Alternatives (free-tier / lower-cost swaps).
    "fly": _fly,
    "render": _render,
    "cloudflare_pages": _cloudflare_pages,
    "netlify": _netlify,
    "supabase": _supabase,
    "memgraph_cloud": _memgraph_cloud,
    "turbopuffer": _turbopuffer,
    "pinecone": _pinecone,
    "pgvector": _pgvector,
    "redis_cloud": _redis_cloud,
    "runpod_serverless": _runpod_serverless,
    "replicate": _replicate,
    "fly_gpu": _fly_gpu,
    "backblaze_b2": _backblaze_b2,
    "aws_s3": _aws_s3,
    "workos": _workos,
    "better_auth": _better_auth,
    "glitchtip": _glitchtip,
    "better_stack": _better_stack,
    "grafana_cloud": _grafana_cloud,
    "plausible": _plausible,
    "langsmith": _langsmith,
    "postmark": _postmark,
    "inngest": _inngest,
}


# ---------------------------------------------------------------------------
# Kernel handoffs — Hermes. Always emitted, one per engine.
# ---------------------------------------------------------------------------


def _hermes_in_process() -> ServiceHandoff:
    return ServiceHandoff(
        slug="hermes_in_process",
        role="kernel",
        secrets=[],  # Reuses the platform's DATABASE_URL.
        steps=[
            {
                "title": "Run Hermes SQL migrations against the platform Postgres",
                "cmd": (
                    "psql \"${DATABASE_URL}\" -v ON_ERROR_STOP=1 -f "
                    "nexus-platform/hermes/migrations/0001_jobs_and_agents.sql"
                ),
            },
            {
                "title": "Enable LISTEN/NOTIFY channels used by the in-process dispatcher",
                "cmd": (
                    "psql \"${DATABASE_URL}\" -v ON_ERROR_STOP=1 -c "
                    "\"SELECT pg_notify('hermes_boot', 'ok');\" > /dev/null && echo OK"
                ),
            },
            {
                "title": "Set HERMES_ENGINE=in_process on the platform service",
                "cmd": (
                    "echo 'export HERMES_ENGINE=in_process' >> nexus.env"
                ),
            },
        ],
    )


def _hermes_temporal_cloud() -> ServiceHandoff:
    return ServiceHandoff(
        slug="hermes_temporal_cloud",
        role="kernel",
        secrets=[
            "TEMPORAL_CLOUD_NAMESPACE",
            "TEMPORAL_CLOUD_API_KEY",
            "TEMPORAL_CLOUD_ADDRESS",
        ],
        steps=[
            {
                "title": "Verify the Temporal Cloud namespace exists (idempotent)",
                "cmd": (
                    "temporal --address ${TEMPORAL_CLOUD_ADDRESS} "
                    "--namespace ${TEMPORAL_CLOUD_NAMESPACE} "
                    "--tls --api-key ${TEMPORAL_CLOUD_API_KEY} "
                    "operator namespace describe > /dev/null && echo NAMESPACE_OK"
                ),
            },
            {
                "title": "Register the Hermes task queues (agents, dispatch, events)",
                "cmd": (
                    "for q in hermes-agents hermes-dispatch hermes-events; do "
                    "temporal --address ${TEMPORAL_CLOUD_ADDRESS} "
                    "--namespace ${TEMPORAL_CLOUD_NAMESPACE} "
                    "--tls --api-key ${TEMPORAL_CLOUD_API_KEY} "
                    "task-queue describe --task-queue $q > /dev/null 2>&1 || true; done"
                ),
            },
            {
                "title": "Set Hermes engine env vars on the platform service",
                "cmd": (
                    "{ echo 'export HERMES_ENGINE=temporal_cloud'; "
                    "echo 'export TEMPORAL_CLOUD_NAMESPACE='${TEMPORAL_CLOUD_NAMESPACE}; "
                    "echo 'export TEMPORAL_CLOUD_ADDRESS='${TEMPORAL_CLOUD_ADDRESS}; } "
                    ">> nexus.env"
                ),
            },
        ],
    )


def _hermes_temporal_selfhost() -> ServiceHandoff:
    return ServiceHandoff(
        slug="hermes_temporal_selfhost",
        role="kernel",
        secrets=["TEMPORAL_HOST", "TEMPORAL_NAMESPACE"],
        steps=[
            {
                "title": "Boot the Temporal single-node stack (docker compose)",
                "cmd": (
                    "docker compose -f nexus-platform/hermes/docker-compose.temporal.yml "
                    "up -d --wait"
                ),
            },
            {
                "title": "Create the Hermes namespace on the self-hosted cluster (idempotent)",
                "cmd": (
                    "temporal --address ${TEMPORAL_HOST} operator namespace create "
                    "--namespace ${TEMPORAL_NAMESPACE} "
                    "--retention 72h 2>/dev/null || true"
                ),
            },
            {
                "title": "Set Hermes engine env vars on the platform service",
                "cmd": (
                    "{ echo 'export HERMES_ENGINE=temporal_selfhost'; "
                    "echo 'export TEMPORAL_HOST='${TEMPORAL_HOST}; "
                    "echo 'export TEMPORAL_NAMESPACE='${TEMPORAL_NAMESPACE}; } "
                    ">> nexus.env"
                ),
            },
        ],
    )


_HERMES_BUILDERS: dict[str, Callable[[], ServiceHandoff]] = {
    "in_process":         _hermes_in_process,
    "temporal_cloud":     _hermes_temporal_cloud,
    "temporal_selfhost":  _hermes_temporal_selfhost,
}


def hermes_handoff(engine: str) -> ServiceHandoff:
    """Return the handoff for the chosen Hermes engine. Never None —
    Hermes is kernel-mandatory."""
    builder = _HERMES_BUILDERS.get(engine)
    if builder is None:
        raise ValueError(f"Unknown Hermes engine: {engine!r}")
    return builder()


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
    # Kernel first — Hermes must be online before any app_compute step
    # runs, because the platform boot script reads HERMES_ENGINE from
    # nexus.env and refuses to start without it.
    out.append(hermes_handoff(stack.kernel.hermes.engine))
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
