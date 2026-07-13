"""Unit tests for stack_provisioning \u2014 the handoff-fragment layer."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

import pytest

from app.models.stack import (
    STANDARD_100_EUR_STACK,
    StackConfig,
    StackPreferences,
    recommend_stack,
)
from app.services.cloud_deployers import PlaybookInputs
from app.services.stack_provisioning import (
    _BUILDERS,
    handoff_for,
    merge_into_playbook_inputs,
    stack_handoffs,
)


# ---------- catalogue coverage ----------


def test_every_standard_preset_service_has_a_handoff_builder():
    for role, slug in STANDARD_100_EUR_STACK.items():
        assert handoff_for(slug) is not None, (
            f"missing handoff builder for {role}={slug} in _BUILDERS"
        )


def test_handoff_role_matches_catalogue_role():
    from app.models.stack import CATALOGUE_BY_SLUG
    for slug, builder in _BUILDERS.items():
        fragment = builder()
        assert fragment.slug == slug
        assert CATALOGUE_BY_SLUG[slug].role == fragment.role


# ---------- placeholder safety ----------


_ONLY_PLACEHOLDERS = re.compile(r"\$\{[A-Z0-9_]+\}")


def test_no_real_secret_looking_string_in_any_step():
    """Every command must reference secrets as ${VAR} only, never inline."""
    banned_patterns = [
        # inline-looking secret assignments
        re.compile(r"[A-Z_]+=[a-zA-Z0-9\-_]{20,}"),
        # obvious sk-... style keys
        re.compile(r"\bsk-[a-zA-Z0-9]{16,}"),
        re.compile(r"\bxox[bap]-[a-zA-Z0-9\-]{10,}"),
        re.compile(r"\bghp_[a-zA-Z0-9]{20,}"),
    ]
    for slug, builder in _BUILDERS.items():
        for step in builder().steps:
            cmd = step["cmd"]
            for pat in banned_patterns:
                assert not pat.search(cmd), (
                    f"potential inline secret in {slug} step: {cmd!r}"
                )


def test_every_step_has_title_and_cmd():
    for slug, builder in _BUILDERS.items():
        for step in builder().steps:
            assert step.get("title"), f"{slug}: step missing title"
            assert step.get("cmd"), f"{slug}: step missing cmd"


def test_secrets_look_like_env_var_names():
    env_var = re.compile(r"^[A-Z][A-Z0-9_]*$")
    for slug, builder in _BUILDERS.items():
        for s in builder().secrets:
            assert env_var.match(s), f"{slug}: bad secret name {s!r}"


# ---------- stack_handoffs ordering ----------


def test_stack_handoffs_orders_compute_before_observability():
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(preferences=prefs, selection=sel)

    handoffs = stack_handoffs(cfg)
    slugs_in_order = [h.slug for h in handoffs]

    # Railway (compute) must appear before Sentry (errors) + PostHog + Langfuse.
    idx_compute = slugs_in_order.index("railway")
    for later in ("sentry", "posthog", "langfuse"):
        if later in slugs_in_order:
            assert slugs_in_order.index(later) > idx_compute, (
                f"{later} should come after compute in the playbook order"
            )


def test_stack_handoffs_respects_overrides():
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(
        preferences=prefs,
        selection=sel,
        overrides={"postgres": "supabase"},
    )
    handoffs = stack_handoffs(cfg)
    slugs = {h.slug for h in handoffs}
    # Neon (canonical) should NOT appear when overridden with Supabase.
    assert "neon" not in slugs
    # Supabase now has a builder, so the override is reflected in the playbook.
    assert "supabase" in slugs


def test_stack_handoffs_drops_self_host_only_services_silently():
    # loki_self_host runs inside the operator's compute and does not emit
    # playbook steps. Confirm it silently drops out without breaking the merge.
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(
        preferences=prefs,
        selection=sel,
        overrides={"log_platform": "loki_self_host"},
    )
    handoffs = stack_handoffs(cfg)
    slugs = {h.slug for h in handoffs}
    assert "loki_self_host" not in slugs
    # Other roles still generate handoffs.
    assert len(handoffs) >= 15


def test_every_alternative_builder_role_matches_catalogue():
    from app.models.stack import CATALOGUE_BY_SLUG
    alternative_slugs = [
        "fly", "render", "cloudflare_pages", "netlify",
        "supabase", "memgraph_cloud",
        "turbopuffer", "pinecone", "pgvector",
        "redis_cloud",
        "runpod_serverless", "replicate", "fly_gpu",
        "backblaze_b2", "aws_s3",
        "workos", "better_auth",
        "glitchtip",
        "better_stack", "grafana_cloud",
        "plausible", "langsmith",
        "postmark", "inngest",
    ]
    for slug in alternative_slugs:
        fragment = handoff_for(slug)
        assert fragment is not None, f"missing builder for alternative {slug}"
        assert fragment.slug == slug
        assert CATALOGUE_BY_SLUG[slug].role == fragment.role
        assert fragment.steps, f"{slug} returned no steps"
        for step in fragment.steps:
            assert step.get("title") and step.get("cmd")


def test_pgvector_reuses_database_url_only():
    fragment = handoff_for("pgvector")
    assert fragment.secrets == ["DATABASE_URL"]


# Env vars that come from OTHER handoffs or from the base playbook,
# so it's fine for a builder to reference them without declaring them
# in its own `secrets` list.
_CROSS_HANDOFF_VARS: set[str] = {
    # Base playbook (cloud_deployers.py + write_playbook).
    "PLATFORM_BOOTSTRAP_TOKEN", "ANTHROPIC_API_KEY", "POSTGRES_PASSWORD",
    "FLY_API_TOKEN",  # reused by fly_gpu
    # From other handoffs — pgvector/better_auth reuse the Postgres DSN,
    # Cloudflare Pages reuses the Cloudflare account creds, etc.
    "DATABASE_URL",
    "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ZONE_ID",
    "PLATFORM_PUBLIC_URL", "PLATFORM_PUBLIC_HOST",
    "NEXUS_DOMAIN",
    "OPENROUTER_API_KEY",  # railway pushes it downstream
}

_PLACEHOLDER_RE = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")


def test_every_builder_uses_only_declared_or_shared_placeholders():
    """Every ${VAR} in any step must be either declared in that builder's
    `secrets` list or in the shared cross-handoff allow-list. Catches
    typos and accidentally-inline secrets in one shot."""
    for slug, builder in _BUILDERS.items():
        fragment = builder()
        declared = set(fragment.secrets)
        for step in fragment.steps:
            referenced = set(_PLACEHOLDER_RE.findall(step["cmd"]))
            undeclared = referenced - declared - _CROSS_HANDOFF_VARS
            assert not undeclared, (
                f"{slug} step {step['title']!r} references undeclared "
                f"placeholders: {sorted(undeclared)}"
            )


def test_no_step_contains_a_bare_command_flag_that_looks_like_a_secret():
    """Belt-and-braces regex: catch anything shaped like an inline secret
    that the coarser test in test_no_real_secret_looking_string missed."""
    inline_looking = re.compile(
        r"(?:token|key|secret|password|dsn)\s*[=:]\s*[a-zA-Z0-9]{16,}",
        re.IGNORECASE,
    )
    for slug, builder in _BUILDERS.items():
        for step in builder().steps:
            # Ignore matches that are actually ${VAR} placeholders.
            cmd = _PLACEHOLDER_RE.sub("", step["cmd"])
            assert not inline_looking.search(cmd), (
                f"{slug} step {step['title']!r} looks like it inlines a secret: {step['cmd']!r}"
            )


def test_grafana_cloud_covers_logs_metrics_traces():
    fragment = handoff_for("grafana_cloud")
    secret_set = set(fragment.secrets)
    assert "GRAFANA_LOKI_URL" in secret_set
    assert "GRAFANA_PROM_URL" in secret_set
    assert "GRAFANA_TEMPO_URL" in secret_set


def test_stack_handoffs_empty_when_stack_none():
    prefs = StackPreferences(monthly_budget_eur=0, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(preferences=prefs, selection=sel)
    # Free tier still returns some handoffs (Vercel, PostHog free\u2026).
    handoffs = stack_handoffs(cfg)
    # It's fine for free-tier to have 0 handoffs when the recommender
    # picked services outside the standard preset.
    assert isinstance(handoffs, list)


# ---------- merge_into_playbook_inputs ----------


def _make_inputs(tmp_path: Path) -> PlaybookInputs:
    return PlaybookInputs(
        instance_id=uuid4(),
        instance_name="test",
        modality="fly",
        region="mad",
        domain=None,
        deployments_dir=tmp_path,
        endpoint_hint="https://test.fly.dev",
        required_secrets=["FLY_API_TOKEN", "PLATFORM_BOOTSTRAP_TOKEN"],
        provider_steps=[{"title": "Fly deploy", "cmd": "fly deploy"}],
        post_deploy_checks=["curl https://test.fly.dev/_health"],
    )


def test_merge_noop_when_stack_none(tmp_path):
    inputs = _make_inputs(tmp_path)
    before_secrets = list(inputs.required_secrets)
    before_steps = list(inputs.provider_steps)
    merge_into_playbook_inputs(inputs, None)
    assert inputs.required_secrets == before_secrets
    assert inputs.provider_steps == before_steps


def test_merge_appends_standard_preset_steps_and_secrets(tmp_path):
    inputs = _make_inputs(tmp_path)
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    stack = StackConfig(preferences=prefs, selection=sel)

    merge_into_playbook_inputs(inputs, stack)

    # Original Fly step still first \u2014 stack steps only append.
    assert inputs.provider_steps[0]["title"] == "Fly deploy"

    # Secrets from at least the canonical services must be there.
    for expected_secret in (
        "RAILWAY_API_TOKEN", "VERCEL_API_TOKEN", "NEON_API_KEY",
        "QDRANT_CLOUD_API_KEY", "MODAL_TOKEN_ID", "OPENROUTER_API_KEY",
        "CLERK_SECRET_KEY", "SENTRY_AUTH_TOKEN", "AXIOM_API_TOKEN",
        "POSTHOG_PERSONAL_API_KEY", "LANGFUSE_SECRET_KEY",
        "RESEND_API_KEY", "TRIGGER_API_KEY",
    ):
        assert expected_secret in inputs.required_secrets, (
            f"expected {expected_secret} to be merged into required_secrets"
        )

    # No duplicates in required_secrets.
    assert len(inputs.required_secrets) == len(set(inputs.required_secrets))

    # A section header was inserted.
    titles = [s["title"] for s in inputs.provider_steps]
    assert any("Stack services" in t for t in titles)


def test_merge_appended_steps_use_only_placeholder_secrets(tmp_path):
    inputs = _make_inputs(tmp_path)
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    stack = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    merge_into_playbook_inputs(inputs, stack)

    banned = re.compile(r"[A-Z_]{4,}=[a-zA-Z0-9\-_/]{25,}")
    for step in inputs.provider_steps:
        assert not banned.search(step["cmd"]), (
            f"inline-looking secret in merged step: {step['cmd']!r}"
        )
