# Structural validation for the real-estate vertical: workflow manifests,
# their cross-references into the template catalogue, and a guard against
# hard-coded secrets in the vertical's cards and workflows.
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "agent_templates"
RE_CARDS_DIR = TEMPLATES_DIR / "verticals" / "real-estate"
WORKFLOWS_DIR = TEMPLATES_DIR / "workflows" / "real_estate"

VAR_RE = re.compile(r"^\$\{[A-Z_][A-Z0-9_]*\}$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", flags=re.DOTALL)

REQUIRED_WORKFLOW_KEYS: frozenset[str] = frozenset(
    {
        "id", "version", "vertical", "trigger", "participants", "steps",
        "state_payload", "human_approval_gates", "sla", "retries",
        "terminal_states", "audit_events", "outputs", "notes",
    }
)
REQUIRED_STEP_KEYS: frozenset[str] = frozenset(
    {"order", "name", "template_id", "input_state", "output_state", "retries"}
)

# Secret-shaped assignment whose value is a quoted literal that is NOT a ${VAR}.
SECRET_ASSIGN_RE = re.compile(
    r"(?i)(api[_-]?key|secret[_-]?key|password|passwd|access[_-]?key|"
    r"private[_-]?key|bearer)\s*[:=]\s*(?!\$\{)['\"][A-Za-z0-9/+=_\-]{8,}['\"]"
)


def _card_ids() -> set[str]:
    ids: set[str] = set()
    for path in TEMPLATES_DIR.rglob("*.md"):
        if path.name in {"README.md", "_schema.md"}:
            continue
        m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = yaml.safe_load(m.group(1))
        if isinstance(fm, dict) and "id" in fm:
            ids.add(fm["id"])
    return ids


def _manifests() -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.json")):
        if path.name == "manifest.json":
            continue
        out.append((path, json.loads(path.read_text(encoding="utf-8"))))
    return out


CARD_IDS = _card_ids()
MANIFESTS = _manifests()


def test_workflows_directory_exists() -> None:
    assert WORKFLOWS_DIR.is_dir(), "real-estate workflows directory missing"
    assert MANIFESTS, "no workflow manifests found"


def test_at_least_seven_workflows() -> None:
    assert len(MANIFESTS) >= 7, f"expected >=7 workflows, found {len(MANIFESTS)}"


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_manifest_has_required_keys(path: Path, wf: dict) -> None:
    missing = REQUIRED_WORKFLOW_KEYS - wf.keys()
    assert not missing, f"{path.name} missing keys: {missing}"
    assert wf["vertical"] == "real-estate", f"{path.name}: wrong vertical"
    assert wf["id"] == path.stem, f"{path.name}: id must match filename"


def test_workflow_ids_are_unique() -> None:
    ids = [wf["id"] for _, wf in MANIFESTS]
    dups = {i for i in ids if ids.count(i) > 1}
    assert not dups, f"duplicate workflow ids: {dups}"


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_steps_are_ordered_and_wellformed(path: Path, wf: dict) -> None:
    steps = wf["steps"]
    assert steps, f"{path.name}: no steps"
    orders = [s["order"] for s in steps]
    assert orders == list(range(1, len(steps) + 1)), (
        f"{path.name}: step order must be contiguous 1..N, got {orders}"
    )
    for s in steps:
        missing = REQUIRED_STEP_KEYS - s.keys()
        assert not missing, f"{path.name} step {s.get('name')} missing {missing}"


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_participants_reference_real_cards(path: Path, wf: dict) -> None:
    for pid in wf["participants"]:
        assert pid in CARD_IDS, (
            f"{path.name}: participant {pid!r} is not a known template id"
        )
    # Every step template must also be a participant and a real card.
    for s in wf["steps"]:
        tid = s["template_id"]
        assert tid in CARD_IDS, f"{path.name}: step template {tid!r} unknown"
        assert tid in wf["participants"], (
            f"{path.name}: step template {tid!r} not listed in participants"
        )


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_human_gates_are_consistent(path: Path, wf: dict) -> None:
    declared = set(wf["human_approval_gates"])
    from_steps = {
        s["human_approval_gate"]["gate_id"]
        for s in wf["steps"]
        if "human_approval_gate" in s
    }
    assert declared == from_steps, (
        f"{path.name}: declared gates {declared} != step gates {from_steps}"
    )
    for s in wf["steps"]:
        gate = s.get("human_approval_gate")
        if gate is not None:
            assert gate.get("required") is True, (
                f"{path.name}: gate {gate.get('gate_id')} must be required"
            )


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_slas_use_env_placeholders(path: Path, wf: dict) -> None:
    assert wf["sla"], f"{path.name}: sla block is empty"
    for key, val in wf["sla"].items():
        assert VAR_RE.match(str(val)), (
            f"{path.name}: SLA {key}={val!r} must be a ${{VAR}} placeholder"
        )


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_terminal_states_present(path: Path, wf: dict) -> None:
    assert "completed" in wf["terminal_states"]
    assert "failed" in wf["terminal_states"]
    assert wf["outputs"].get("success") and wf["outputs"].get("failure")


@pytest.mark.parametrize("path,wf", MANIFESTS, ids=[p.stem for p, _ in MANIFESTS])
def test_manifest_version_matches_catalog(path: Path, wf: dict) -> None:
    catalog = json.loads((TEMPLATES_DIR / "catalog.json").read_text(encoding="utf-8"))
    assert wf["version"] == catalog["version"], (
        f"{path.name}: workflow version {wf['version']} != catalog "
        f"{catalog['version']}"
    )


def test_workflow_markdown_docs_have_no_frontmatter() -> None:
    # Workflow docs must NOT be parsed as artifact cards.
    for path in WORKFLOWS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert not FRONTMATTER_RE.match(text), (
            f"{path.name}: workflow doc must not start with YAML frontmatter"
        )


def _vertical_files() -> list[Path]:
    files = list(RE_CARDS_DIR.glob("re_*.md"))
    files += list(WORKFLOWS_DIR.glob("*.json"))
    files += list(WORKFLOWS_DIR.glob("*.md"))
    return files


@pytest.mark.parametrize("path", _vertical_files(), ids=lambda p: p.name)
def test_no_hardcoded_secrets(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    hit = SECRET_ASSIGN_RE.search(text)
    assert hit is None, (
        f"{path}: looks like a hard-coded secret: {hit.group(0)!r}. "
        f"Use a ${{VAR}} placeholder resolved from nexus.secrets.env."
    )


def test_expected_new_real_estate_cards_present() -> None:
    # The vertical must ship its agents/sidecars/skills as real cards.
    got = {p.stem for p in RE_CARDS_DIR.glob("re_*.md")}
    assert len(got) >= 42, f"expected >=42 new real-estate cards, found {len(got)}"
