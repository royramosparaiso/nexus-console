# Sanity checks for the agent-template catalogue and the bundled
# spike-ramp scenario. These are documentation-shaped assets, so the
# tests only enforce structural invariants — not semantics.
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "agent_templates"
SPIKE_SCENARIO = REPO_ROOT / "deploy" / "hermes" / "scenarios" / "spike-ramp.json"

# The catalogue's README table lists these — every one must exist as a
# real markdown file. Guarantees the table doesn't drift silently.
EXPECTED_TEMPLATES: tuple[str, ...] = (
    "market_research_analyst",
    "fundamental_analyst",
    "macro_context_agent",
    "bull_bear_debate_pair",
    "risk_committee",
    "memory_reflector",
)


def test_templates_readme_exists() -> None:
    assert (TEMPLATES_DIR / "README.md").is_file()


@pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
def test_each_template_file_exists_and_has_required_sections(name: str) -> None:
    path = TEMPLATES_DIR / f"{name}.md"
    assert path.is_file(), f"missing template: {path}"

    body = path.read_text(encoding="utf-8")

    # Structural invariants every template card must satisfy so that
    # the catalogue is uniform enough to be consumed by tooling later.
    for section in ("## Identity", "## Purpose", "## Wiring"):
        assert section in body, f"{name}.md is missing section: {section}"


def test_readme_lists_every_template() -> None:
    body = (TEMPLATES_DIR / "README.md").read_text(encoding="utf-8")
    for name in EXPECTED_TEMPLATES:
        assert f"`{name}`" in body, f"README does not reference template {name!r}"


# --- spike scenario ---------------------------------------------------


def test_spike_scenario_is_wellformed_json() -> None:
    payload = json.loads(SPIKE_SCENARIO.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert "steps" in payload and "workflow" in payload


def test_spike_scenario_is_monotonically_increasing() -> None:
    # The "spike" character of the scenario depends on each step
    # cranking the rate up, never down.
    payload = json.loads(SPIKE_SCENARIO.read_text(encoding="utf-8"))
    rates = [step["ratePerSecond"] for step in payload["steps"]]
    assert rates == sorted(rates)
    assert rates[0] < rates[-1], "spike scenario should ramp, not plateau"
    assert rates[-1] >= 100, "top step should be a real spike (>=100 wf/s)"


def test_spike_scenario_workflow_matches_taskqueue_convention() -> None:
    # maru's basic-workflow expects to run on the temporal-basic
    # queue that the docker-compose stacks register.
    payload = json.loads(SPIKE_SCENARIO.read_text(encoding="utf-8"))
    assert payload["workflow"]["taskQueue"] == "temporal-basic"
    assert payload["workflow"]["args"]["sequenceCount"] >= 1
