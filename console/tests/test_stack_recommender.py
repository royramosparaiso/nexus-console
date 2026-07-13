"""Unit tests for the stack catalogue + recommender."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.stack import (
    CATALOGUE,
    CATALOGUE_BY_SLUG,
    STANDARD_100_EUR_STACK,
    StackPreferences,
    StackSelection,
    recommend_stack,
    services_for_role,
    _tier_from_budget,
)
from app.models.wizard import WizardSubmission


# ---------- catalogue integrity ----------


def test_catalogue_slugs_are_unique():
    slugs = [s.slug for s in CATALOGUE]
    assert len(slugs) == len(set(slugs)), "duplicate slugs in catalogue"


def test_standard_stack_slugs_all_exist():
    for role, slug in STANDARD_100_EUR_STACK.items():
        svc = CATALOGUE_BY_SLUG[slug]
        assert svc.role == role, f"{slug} has role {svc.role}, not {role}"


def test_every_role_has_at_least_one_service():
    for role in STANDARD_100_EUR_STACK.keys():
        assert services_for_role(role), f"no service for role {role}"


# ---------- tier bucketing ----------


@pytest.mark.parametrize("budget,expected", [
    (0, "free"),
    (10, "free"),
    (25, "hobby"),
    (60, "standard"),
    (100, "standard"),
    (150, "standard"),
    (250, "scale"),
])
def test_tier_from_budget(budget, expected):
    assert _tier_from_budget(budget) == expected


# ---------- recommender behaviour ----------


def test_recommend_100_eur_matches_canonical_standard_stack():
    """~100 EUR + cloud + defaults → returns the canonical standard stack."""
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    assert sel.tier == "standard"
    for role, expected_slug in STANDARD_100_EUR_STACK.items():
        # graph_db + gpu + observability + analytics + jobs + email are
        # gated by feature flags; the default prefs enable them.
        assert sel.services.get(role) == expected_slug, (
            f"role {role}: got {sel.services.get(role)}, expected {expected_slug}"
        )


def test_recommend_local_prefers_self_hostable():
    prefs = StackPreferences(monthly_budget_eur=0, deployment_mode="local")
    sel = recommend_stack(prefs)
    # Every returned service must be self-hostable in local mode.
    for role, slug in sel.services.items():
        svc = CATALOGUE_BY_SLUG[slug]
        assert svc.self_hostable, (
            f"local mode returned non-self-hostable {slug} for {role}"
        )


def test_recommend_disable_feature_flags_drops_roles():
    prefs = StackPreferences(
        monthly_budget_eur=100,
        deployment_mode="cloud",
        needs_graph_db=False,
        needs_voice_gpu=False,
        needs_product_analytics=False,
        needs_background_jobs=False,
        needs_llm_observability=False,
    )
    sel = recommend_stack(prefs)
    # Optional roles must be absent.
    for absent in ("graph_db", "gpu_serverless", "product_analytics",
                   "background_jobs", "llm_observability"):
        assert absent not in sel.services, f"expected {absent} to be dropped"
    # Core roles must remain.
    for present in ("app_compute", "postgres", "vector_db", "ci_cd"):
        assert present in sel.services


def test_recommend_hobby_prefers_grafana_cloud_over_axiom():
    from app.models.stack import StackPreferences, recommend_stack

    prefs = StackPreferences(
        monthly_budget_eur=30,   # hobby tier
        deployment_mode="cloud",
        prefer_open_source=False,
    )
    sel = recommend_stack(prefs)
    assert sel.tier == "hobby"
    assert sel.services.get("log_platform") == "grafana_cloud", (
        "hobby tier should prefer Grafana Cloud — same 0 EUR entry price "
        "but bundles logs + metrics + traces"
    )


def test_recommend_hobby_override_is_skipped_when_service_removed():
    """Sanity: if grafana_cloud lost its 'hobby' tier, the override
    should silently fall through instead of returning an invalid pick."""
    from app.models.stack import (
        CATALOGUE_BY_SLUG, StackPreferences, recommend_stack,
    )

    grafana = CATALOGUE_BY_SLUG["grafana_cloud"]
    original_tiers = grafana.tiers
    try:
        # Strip 'hobby' — the override guard should now fall back.
        object.__setattr__(grafana, "tiers", [t for t in original_tiers if t != "hobby"])
        prefs = StackPreferences(monthly_budget_eur=30, deployment_mode="cloud")
        sel = recommend_stack(prefs)
        assert sel.tier == "hobby"
        # Falls back to the cheapest hobby-eligible option — not grafana_cloud.
        assert sel.services.get("log_platform") != "grafana_cloud"
    finally:
        object.__setattr__(grafana, "tiers", original_tiers)


def test_recommend_standard_still_uses_axiom():
    from app.models.stack import StackPreferences, recommend_stack

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    # Canonical 100-EUR stack keeps Axiom — the hobby override is
    # scoped to hobby tier only.
    assert sel.services["log_platform"] == "axiom"


def test_recommend_free_tier_stays_under_budget():
    prefs = StackPreferences(monthly_budget_eur=10, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    assert sel.tier == "free"
    # Loose bound: free-tier picks should aggregate to well below 25 USD.
    assert sel.estimated_monthly_usd < 25, sel.estimated_monthly_usd


def test_recommend_scale_tier_uses_scale_prices():
    prefs = StackPreferences(monthly_budget_eur=400, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    assert sel.tier == "scale"
    # At scale tier the total is dominated by scale prices; must exceed
    # 100 USD across a full stack.
    assert sel.estimated_monthly_usd > 100, sel.estimated_monthly_usd


# ---------- HTTP endpoints ----------


client = TestClient(app)


def test_catalog_endpoint_lists_every_service():
    r = client.get("/wizard/stack/catalog")
    assert r.status_code == 200
    data = r.json()
    assert len(data["services"]) == len(CATALOGUE)
    assert set(data["by_role"].keys()) >= set(STANDARD_100_EUR_STACK.keys())
    assert data["standard_100_eur_stack"] == STANDARD_100_EUR_STACK


def test_recommend_endpoint_returns_standard_stack_for_100_eur():
    r = client.post(
        "/wizard/stack/recommend",
        json={"monthly_budget_eur": 100, "deployment_mode": "cloud"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tier"] == "standard"
    assert data["services"]["app_compute"] == "railway"
    assert data["services"]["postgres"] == "neon"
    assert data["services"]["gpu_serverless"] == "modal"


def test_recommend_endpoint_rejects_negative_budget():
    r = client.post(
        "/wizard/stack/recommend",
        json={"monthly_budget_eur": -1, "deployment_mode": "cloud"},
    )
    assert r.status_code == 422


# ---------- WizardSubmission carries StackConfig through YAML ----------


def _make_submission(stack):
    return WizardSubmission(
        instance_name="nexus-yaml-labels",
        persona={"display_name": "Test", "kind": "personal"},
        deployment={"modality": "fly"},
        llms={
            "enabled_providers": ["anthropic"],
            "roles": {
                "planner": "anthropic:claude-3-5-sonnet",
                "coordinator": "anthropic:claude-3-5-sonnet",
                "worker": "anthropic:claude-3-5-haiku",
                "embeddings": "openai:text-embedding-3-small",
            },
            "monthly_budget_usd": 50,
        },
        memory={"driver": "postgres_pgvector"},
        areas={"enabled": ["personal_organization"]},
        governance={},
        stack=stack,
    )


def test_yaml_labels_services_as_builder_or_manual():
    from app.models.stack import StackConfig
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    yaml_text = render_instance_yaml(_make_submission(cfg))

    assert "handoff: builder" in yaml_text
    for role, slug in cfg.effective_services().items():
        assert f"{role}: {{ slug: {slug}," in yaml_text
    assert "handoff_summary:" in yaml_text
    assert "automated:" in yaml_text


def test_yaml_labels_self_host_only_service_as_manual():
    from app.models.stack import StackConfig
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(
        preferences=prefs, selection=sel,
        overrides={"log_platform": "loki_self_host"},
    )
    yaml_text = render_instance_yaml(_make_submission(cfg))

    assert "log_platform: { slug: loki_self_host, handoff: manual }" in yaml_text
    assert "manual:" in yaml_text
    assert "log_platform=loki_self_host" in yaml_text


def test_submission_with_stack_renders_yaml_section():
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    selection = recommend_stack(prefs)
    from app.models.stack import StackConfig

    stack = StackConfig(preferences=prefs, selection=selection)
    sub = WizardSubmission(
        instance_name="test-instance",
        persona={"display_name": "Test", "kind": "personal"},
        deployment={"modality": "fly"},
        llms={
            "enabled_providers": ["anthropic"],
            "roles": {
                "planner": "anthropic:claude-3-5-sonnet",
                "coordinator": "anthropic:claude-3-5-sonnet",
                "worker": "anthropic:claude-3-5-haiku",
                "embeddings": "openai:text-embedding-3-small",
            },
            "monthly_budget_usd": 50,
        },
        memory={"driver": "postgres_pgvector"},
        areas={"enabled": ["personal_organization", "meetings"]},
        governance={},
        stack=stack,
    )
    yaml = render_instance_yaml(sub)
    assert "stack:" in yaml
    assert "tier: standard" in yaml
    assert "app_compute: { slug: railway," in yaml
    assert "postgres: { slug: neon," in yaml


def test_submission_without_stack_still_valid():
    sub = WizardSubmission(
        instance_name="legacy",
        persona={"display_name": "Legacy", "kind": "personal"},
        deployment={"modality": "local"},
        llms={
            "enabled_providers": ["ollama"],
            "roles": {
                "planner": "ollama:llama3.1",
                "coordinator": "ollama:llama3.1",
                "worker": "ollama:llama3.1",
                "embeddings": "ollama:nomic-embed-text",
            },
            "monthly_budget_usd": 0,
        },
        memory={"driver": "sqlite"},
        areas={"enabled": ["personal_organization"]},
        governance={},
    )
    assert sub.stack is None


# ---------- override validation ----------


def test_stack_config_override_wrong_role_raises():
    from app.models.stack import StackConfig
    with pytest.raises(ValueError):
        StackConfig(
            selection=StackSelection(),
            overrides={"postgres": "modal"},  # modal is GPU, not postgres
        )


def test_effective_services_applies_overrides():
    from app.models.stack import StackConfig
    prefs = StackPreferences(monthly_budget_eur=100)
    sel = recommend_stack(prefs)
    cfg = StackConfig(
        preferences=prefs,
        selection=sel,
        overrides={"postgres": "supabase"},
    )
    assert cfg.effective_services()["postgres"] == "supabase"
    assert cfg.effective_services()["app_compute"] == "railway"
