"""Kernel services: Hermes is always deployed, engine tracks tier."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.kernel import (
    HERMES_ENGINE_BY_TIER,
    HermesConfig,
    KernelServices,
    default_kernel_for_tier,
)
from app.models.stack import (
    StackConfig,
    StackPreferences,
    StackSelection,
    recommend_stack,
)
from app.services.stack_provisioning import (
    hermes_handoff,
    stack_handoffs,
)


# ---------------------------------------------------------------------------
# Default engine per tier
# ---------------------------------------------------------------------------


def test_default_engine_hobby_and_standard_are_in_process():
    assert default_kernel_for_tier("hobby").hermes.engine == "in_process"
    assert default_kernel_for_tier("standard").hermes.engine == "in_process"


def test_default_engine_scale_is_temporal_cloud():
    assert default_kernel_for_tier("scale").hermes.engine == "temporal_cloud"


def test_default_engine_unknown_tier_falls_back_to_in_process():
    assert default_kernel_for_tier("nonsense").hermes.engine == "in_process"


def test_engine_by_tier_covers_every_stack_tier():
    for tier in ("free", "hobby", "standard", "scale"):
        assert tier in HERMES_ENGINE_BY_TIER


# ---------------------------------------------------------------------------
# Features contract \u2014 always the same four capabilities.
# ---------------------------------------------------------------------------


def test_hermes_features_are_the_four_kernel_capabilities():
    cfg = HermesConfig()
    assert cfg.features == [
        "agent_registry",
        "durable_job_dispatch",
        "hot_deploy_agents",
        "event_bus",
    ]


def test_hermes_features_are_engine_independent():
    for engine in ("in_process", "temporal_cloud", "temporal_selfhost"):
        cfg = HermesConfig(engine=engine)
        assert set(cfg.features) == {
            "agent_registry",
            "durable_job_dispatch",
            "hot_deploy_agents",
            "event_bus",
        }


# ---------------------------------------------------------------------------
# Required secrets per engine.
# ---------------------------------------------------------------------------


def test_in_process_needs_no_extra_secrets():
    assert HermesConfig(engine="in_process").required_secrets() == []


def test_temporal_cloud_declares_its_three_secrets():
    assert HermesConfig(engine="temporal_cloud").required_secrets() == [
        "TEMPORAL_CLOUD_NAMESPACE",
        "TEMPORAL_CLOUD_API_KEY",
        "TEMPORAL_CLOUD_ADDRESS",
    ]


def test_selfhost_declares_host_and_namespace():
    assert HermesConfig(engine="temporal_selfhost").required_secrets() == [
        "TEMPORAL_HOST",
        "TEMPORAL_NAMESPACE",
    ]


# ---------------------------------------------------------------------------
# StackConfig always carries a kernel, engine snaps to tier.
# ---------------------------------------------------------------------------


def test_stack_config_always_has_kernel_even_when_not_passed():
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    assert cfg.kernel is not None
    assert isinstance(cfg.kernel, KernelServices)


def test_stack_config_scale_tier_auto_promotes_engine_to_temporal_cloud():
    prefs = StackPreferences(monthly_budget_eur=500, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    assert sel.tier == "scale"
    cfg = StackConfig(preferences=prefs, selection=sel)
    assert cfg.kernel.hermes.engine == "temporal_cloud"


def test_stack_config_hobby_tier_keeps_in_process():
    prefs = StackPreferences(monthly_budget_eur=30, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    assert cfg.kernel.hermes.engine == "in_process"


def test_stack_config_never_drops_the_kernel_field():
    # Even when the caller passes overrides for every role, kernel
    # stays intact — it's not toggleable.
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(
        preferences=prefs,
        selection=recommend_stack(prefs),
        overrides={"log_platform": "loki_self_host"},
    )
    assert cfg.kernel.hermes.engine in {
        "in_process", "temporal_cloud", "temporal_selfhost"
    }


# ---------------------------------------------------------------------------
# Handoff builders per engine.
# ---------------------------------------------------------------------------


def test_hermes_handoff_returns_a_fragment_for_every_engine():
    for engine in ("in_process", "temporal_cloud", "temporal_selfhost"):
        h = hermes_handoff(engine)
        assert h.role == "kernel"
        assert h.steps


def test_hermes_handoff_unknown_engine_raises():
    with pytest.raises(ValueError):
        hermes_handoff("wat")


def test_hermes_in_process_reuses_database_url_only():
    h = hermes_handoff("in_process")
    assert h.secrets == []
    # Steps must reference DATABASE_URL (cross-handoff var from the
    # base playbook) but no other secret.
    joined = " ".join(step["cmd"] for step in h.steps)
    assert "${DATABASE_URL}" in joined


def test_hermes_temporal_cloud_declares_and_uses_its_secrets():
    h = hermes_handoff("temporal_cloud")
    assert set(h.secrets) == {
        "TEMPORAL_CLOUD_NAMESPACE",
        "TEMPORAL_CLOUD_API_KEY",
        "TEMPORAL_CLOUD_ADDRESS",
    }
    joined = " ".join(step["cmd"] for step in h.steps)
    for var in h.secrets:
        assert f"${{{var}}}" in joined


def test_hermes_selfhost_boots_docker_compose():
    h = hermes_handoff("temporal_selfhost")
    joined = " ".join(step["cmd"] for step in h.steps)
    assert "docker compose" in joined
    assert "docker-compose.temporal.yml" in joined


def test_hermes_steps_never_inline_secrets():
    inline = re.compile(
        r"(?:token|key|secret|password)\s*[=:]\s*[a-zA-Z0-9]{16,}", re.IGNORECASE
    )
    for engine in ("in_process", "temporal_cloud", "temporal_selfhost"):
        for step in hermes_handoff(engine).steps:
            # Strip ${VAR} placeholders \u2014 they're not inline secrets.
            cmd = re.sub(r"\$\{[A-Z_][A-Z0-9_]*\}", "", step["cmd"])
            assert not inline.search(cmd), f"{engine}: {step['title']!r}"


# ---------------------------------------------------------------------------
# stack_handoffs prepends the kernel step before app_compute.
# ---------------------------------------------------------------------------


def test_stack_handoffs_puts_hermes_first():
    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    fragments = stack_handoffs(cfg)
    assert fragments, "stack_handoffs returned empty"
    assert fragments[0].role == "kernel"
    assert fragments[0].slug.startswith("hermes_")


def test_stack_handoffs_kernel_matches_configured_engine():
    prefs = StackPreferences(monthly_budget_eur=500, deployment_mode="cloud")
    sel = recommend_stack(prefs)
    cfg = StackConfig(preferences=prefs, selection=sel)
    fragments = stack_handoffs(cfg)
    assert fragments[0].slug == "hermes_temporal_cloud"


# ---------------------------------------------------------------------------
# YAML surfaces the kernel block.
# ---------------------------------------------------------------------------


def _make_submission(stack):
    from app.models.wizard import WizardSubmission
    return WizardSubmission(
        instance_name="nexus-kernel-yaml",
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


def test_yaml_emits_kernel_block_with_hermes_features():
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    yaml_text = render_instance_yaml(_make_submission(cfg))

    assert "kernel:" in yaml_text
    assert "hermes:" in yaml_text
    assert "engine: in_process" in yaml_text
    for feat in ("agent_registry", "durable_job_dispatch",
                 "hot_deploy_agents", "event_bus"):
        assert f"- {feat}" in yaml_text


def test_yaml_emits_required_secrets_for_temporal_cloud():
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=500, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    yaml_text = render_instance_yaml(_make_submission(cfg))

    assert "engine: temporal_cloud" in yaml_text
    assert "required_secrets:" in yaml_text
    for var in ("TEMPORAL_CLOUD_NAMESPACE", "TEMPORAL_CLOUD_API_KEY",
                "TEMPORAL_CLOUD_ADDRESS"):
        assert f"- {var}" in yaml_text


def test_yaml_omits_required_secrets_when_in_process():
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    cfg = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    yaml_text = render_instance_yaml(_make_submission(cfg))

    # in_process reuses DATABASE_URL and needs no dedicated secrets \u2014
    # the block must be omitted, not left empty.
    kernel_section = yaml_text.split("kernel:", 1)[1].split("host:", 1)[0]
    assert "required_secrets:" not in kernel_section


# ---------------------------------------------------------------------------
# Wizard endpoint.
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return TestClient(app)


def test_wizard_kernel_endpoint_returns_engine_for_tier(client):
    r = client.get("/wizard/kernel", params={"tier": "scale"})
    assert r.status_code == 200
    body = r.json()
    assert body["kernel"]["hermes"]["engine"] == "temporal_cloud"
    assert body["tier_defaults"]["hobby"] == "in_process"
    assert body["tier_defaults"]["scale"] == "temporal_cloud"
    assert "kernel" in body["rationale"].lower()


def test_wizard_kernel_endpoint_defaults_to_standard(client):
    r = client.get("/wizard/kernel")
    assert r.status_code == 200
    assert r.json()["kernel"]["hermes"]["engine"] == "in_process"
