# Sanity checks for the agent-template catalogue and the bundled
# spike-ramp scenario. These are documentation-shaped assets, so the
# tests only enforce structural invariants — not semantics.
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "agent_templates"
SPIKE_SCENARIO = REPO_ROOT / "deploy" / "hermes" / "scenarios" / "spike-ramp.json"

# The catalogue's README table lists these — every one must exist as a
# real markdown file. Guarantees the table doesn't drift silently.
LEGACY_FINANCE_TEMPLATES: tuple[str, ...] = (
    "market_research_analyst",
    "fundamental_analyst",
    "macro_context_agent",
    "bull_bear_debate_pair",
    "risk_committee",
    "memory_reflector",
)

CATEGORIES: tuple[str, ...] = (
    "intake",
    "market-research",
    "mvs",
    "validation",
    "scaling",
    "investor-deliverable",
    "finance",
)

REQUIRED_FRONTMATTER_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "category",
        "role",
        "mode",
        "depends_on",
        "produces",
        "tools",
        "tags",
        "gate",
        "optional",
    }
)

ALLOWED_ROLES: frozenset[str] = frozenset(
    {"analyst", "judge", "debater", "reflector", "coordinator", "writer", "reviewer", "integrator"}
)

ALLOWED_MODES: frozenset[str] = frozenset(
    {"single-shot", "debate", "pipeline-stage", "gate", "reflector"}
)


def _iter_cards() -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    for path in sorted(TEMPLATES_DIR.rglob("*.md")):
        if path.name in {"README.md", "_schema.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1))
        assert isinstance(fm, dict), f"frontmatter is not a mapping: {path}"
        out.append((path, fm))
    return out


ALL_CARDS = _iter_cards()


def test_catalogue_is_nonempty() -> None:
    assert ALL_CARDS, "no templates found — the catalogue is empty"


def test_templates_readme_exists() -> None:
    assert (TEMPLATES_DIR / "README.md").is_file()


def test_schema_doc_exists() -> None:
    assert (TEMPLATES_DIR / "_schema.md").is_file(), "frontmatter schema doc missing"


@pytest.mark.parametrize("name", LEGACY_FINANCE_TEMPLATES)
def test_legacy_finance_templates_still_exist(name: str) -> None:
    # The v0.12.2 finance catalogue moved into agent_templates/finance/.
    path = TEMPLATES_DIR / "finance" / f"{name}.md"
    assert path.is_file(), f"missing template: {path}"


@pytest.mark.parametrize("path,fm", ALL_CARDS, ids=lambda x: str(x)[:40] if not isinstance(x, dict) else x.get("id", "?"))
def test_every_card_has_required_frontmatter_fields(path: Path, fm: dict) -> None:
    missing = REQUIRED_FRONTMATTER_FIELDS - fm.keys()
    assert not missing, f"{path} is missing frontmatter fields: {missing}"


@pytest.mark.parametrize("path,fm", ALL_CARDS, ids=lambda x: str(x)[:40] if not isinstance(x, dict) else x.get("id", "?"))
def test_every_card_has_required_body_sections(path: Path, fm: dict) -> None:
    body = path.read_text(encoding="utf-8")
    for section in ("## Identity", "## Purpose", "## Wiring"):
        assert section in body, f"{path} is missing section {section}"


def test_frontmatter_categories_are_allowed_and_match_directory() -> None:
    for path, fm in ALL_CARDS:
        cat = fm["category"]
        assert cat in CATEGORIES, f"{path}: category {cat!r} not in {CATEGORIES}"
        assert path.parent.name == cat, (
            f"{path}: category {cat!r} does not match directory {path.parent.name!r}"
        )


def test_frontmatter_roles_and_modes_are_allowed() -> None:
    for path, fm in ALL_CARDS:
        assert fm["role"] in ALLOWED_ROLES, f"{path}: role {fm['role']!r} not allowed"
        assert fm["mode"] in ALLOWED_MODES, f"{path}: mode {fm['mode']!r} not allowed"


def test_frontmatter_id_matches_filename() -> None:
    for path, fm in ALL_CARDS:
        assert fm["id"] == path.stem, f"{path}: id {fm['id']!r} != filename stem {path.stem!r}"
        assert fm["name"] == fm["id"], f"{path}: name {fm['name']!r} != id {fm['id']!r}"


def test_frontmatter_ids_are_unique() -> None:
    ids = [fm["id"] for _, fm in ALL_CARDS]
    dups = {i for i in ids if ids.count(i) > 1}
    assert not dups, f"duplicate template ids: {dups}"


def test_pipeline_steps_are_unique_and_contiguous() -> None:
    # For pipeline templates (non-finance), step must be an integer and
    # every step from 0 through the max must appear exactly once.
    pipeline = [fm for _, fm in ALL_CARDS if fm["category"] != "finance"]
    steps = [fm["step"] for fm in pipeline]
    assert all(isinstance(s, int) for s in steps), f"non-int steps: {steps}"
    assert len(set(steps)) == len(steps), f"duplicate steps: {steps}"
    assert min(steps) == 0
    assert set(steps) == set(range(min(steps), max(steps) + 1)), (
        "pipeline steps must be contiguous"
    )


def test_finance_templates_have_no_pipeline_step() -> None:
    for path, fm in ALL_CARDS:
        if fm["category"] == "finance":
            assert fm.get("step") is None, f"{path}: finance card should have step: null"


def test_depends_on_references_are_valid() -> None:
    ids = {fm["id"] for _, fm in ALL_CARDS}
    for path, fm in ALL_CARDS:
        for ref in fm.get("depends_on") or []:
            assert ref in ids, f"{path}: depends_on references unknown template {ref!r}"


def test_dependencies_point_backwards_in_the_pipeline() -> None:
    # A step-N pipeline template must not depend on a step >= N.
    by_id = {fm["id"]: fm for _, fm in ALL_CARDS}
    for path, fm in ALL_CARDS:
        if fm["category"] == "finance":
            continue
        for ref in fm.get("depends_on") or []:
            upstream = by_id[ref]
            if upstream["category"] == "finance":
                continue
            if upstream.get("step") is None:
                continue
            assert upstream["step"] < fm["step"], (
                f"{path}: depends on {ref} (step {upstream['step']}) "
                f"which is not earlier than self (step {fm['step']})"
            )


def test_gate_flag_only_on_gate_mode_templates() -> None:
    for path, fm in ALL_CARDS:
        if fm.get("gate") is True:
            assert fm["mode"] == "gate", f"{path}: gate=true requires mode=gate"


def test_readme_lists_every_template() -> None:
    body = (TEMPLATES_DIR / "README.md").read_text(encoding="utf-8")
    for _, fm in ALL_CARDS:
        assert f"`{fm['id']}`" in body, (
            f"README does not reference template {fm['id']!r}"
        )


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
