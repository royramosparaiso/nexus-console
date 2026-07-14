#!/usr/bin/env python3
"""Rebuild console/agent_templates/README.md and catalog.json from every card.

Reads every *.md under console/agent_templates/**, parses YAML frontmatter, and
emits:
- README.md   — master index with dual-axis (lifecycle + ops) navigation
- catalog.json — machine-readable catalogue for the Agent Factory UI
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "console" / "agent_templates"
README = ROOT / "README.md"
CATALOG = ROOT / "catalog.json"

# ---------------------------------------------------------------------------
# Ordering / labels
# ---------------------------------------------------------------------------

LIFECYCLE_CATEGORY_ORDER = [
    "intake",
    "market-research",
    "mvs",
    "validation",
    "scaling",
    "investor-deliverable",
    "finance",
]

LIFECYCLE_TITLE = {
    "intake": "Phase 0 · Intake",
    "market-research": "Phase 1 · Market research",
    "mvs": "Phase 2 · Minimal viable setup",
    "validation": "Phase 3 · Market validation",
    "scaling": "Phase 4 · Post-gate scaling",
    "investor-deliverable": "Phase 5 · Investor deliverable",
    "finance": "Standalone · Financial markets (TradingAgents / OpenBB inspired)",
}

OPS_DOMAIN_ORDER = [
    "sales", "deals", "marketing", "operations",
    "intelligence", "customer", "back-office",
]

OPS_DOMAIN_TITLE = {
    "sales": "Sales",
    "deals": "Deals",
    "marketing": "Marketing",
    "operations": "Operations",
    "intelligence": "Intelligence",
    "customer": "Customer",
    "back-office": "Back Office",
}

ROLLOUT_STAGES = ["1-foundation", "2-capture", "3-generate", "4-orchestrate"]
AUTONOMY_LEVELS = ["human-led", "human-assisted", "fully-autonomous"]

VERTICAL_ORDER = ["real-estate", "marketing-agency", "nightclub"]
VERTICAL_TITLE = {
    "real-estate": "Real Estate agency",
    "marketing-agency": "Marketing agency",
    "nightclub": "Night club",
}

ARTIFACT_ORDER = ["agent", "sidecar", "skill"]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def load_all() -> list[tuple[Path, dict]]:
    out = []
    for path in sorted(ROOT.rglob("*.md")):
        if path.name in {"README.md", "_schema.md"}:
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            continue
        # Attach the file path relative to ROOT for the JSON export.
        rel = path.relative_to(ROOT).as_posix()
        fm["_path"] = rel
        out.append((path, fm))
    return out


# ---------------------------------------------------------------------------
# Table renderers
# ---------------------------------------------------------------------------

def _fmt_step(fm: dict) -> str:
    step = fm.get("step")
    return str(step) if step is not None else "—"


def _fmt_flags(fm: dict) -> str:
    flags = []
    if fm.get("gate"):
        flags.append("**gate**")
    if fm.get("optional"):
        flags.append("_optional_")
    return " · ".join(flags) if flags else ""


def _link(fm: dict) -> str:
    return f"[`{fm['id']}`]({fm['_path']})"


def render_lifecycle_table(cards: list[dict]) -> str:
    lines = [
        "| Step | Id | Role | Mode | Produces | Flags |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    cards = sorted(cards, key=lambda c: (c.get("step") if c.get("step") is not None else 999, c["id"]))
    for c in cards:
        lines.append(
            f"| {_fmt_step(c)} | {_link(c)} "
            f"| {c.get('role') or '—'} | {c.get('mode') or '—'} "
            f"| {c.get('produces') or '—'} | {_fmt_flags(c)} |"
        )
    return "\n".join(lines)


def render_ops_matrix(domain_cards: list[dict]) -> str:
    """Grid: rows = rollout_stage, columns = autonomy."""
    by_cell: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in domain_cards:
        stage = c.get("rollout_stage")
        auto = c.get("autonomy")
        if stage and auto:
            by_cell[(stage, auto)].append(c)

    header = "| Rollout \\ Autonomy | " + " | ".join(AUTONOMY_LEVELS) + " |"
    sep = "| --- | " + " | ".join("---" for _ in AUTONOMY_LEVELS) + " |"
    lines = [header, sep]
    for stage in ROLLOUT_STAGES:
        row = [stage]
        for auto in AUTONOMY_LEVELS:
            cards = sorted(by_cell.get((stage, auto), []), key=lambda c: c["id"])
            if not cards:
                row.append("")
                continue
            entries = []
            for c in cards:
                icon = {"agent": "🤖", "sidecar": "⚙️", "skill": "🧩"}.get(c.get("artifact_type"), "•")
                entries.append(f"{icon} {_link(c)}")
            row.append("<br/>".join(entries))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_ops_table(cards: list[dict]) -> str:
    lines = [
        "| Stage | Autonomy | Kind | Id | Role | Mode | Produces |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    cards = sorted(cards, key=lambda c: (c.get("rollout_stage") or "", c.get("autonomy") or "", c["id"]))
    for c in cards:
        lines.append(
            f"| {c.get('rollout_stage') or '—'} | {c.get('autonomy') or '—'} "
            f"| {c.get('artifact_type')} | {_link(c)} "
            f"| {c.get('role') or '—'} | {c.get('mode') or '—'} "
            f"| {c.get('produces') or '—'} |"
        )
    return "\n".join(lines)


def render_role_index(all_cards: list[dict]) -> str:
    by_role: dict[str, list[str]] = defaultdict(list)
    for c in all_cards:
        role = c.get("role") or "—"
        by_role[role].append(c["id"])
    lines = ["| Role | Count | Templates |", "| --- | ---: | --- |"]
    for role in sorted(by_role):
        ids = sorted(set(by_role[role]))
        preview = ", ".join(f"`{i}`" for i in ids[:8])
        if len(ids) > 8:
            preview += f", … (+{len(ids) - 8})"
        lines.append(f"| `{role}` | {len(ids)} | {preview} |")
    return "\n".join(lines)


def render_tag_index(all_cards: list[dict]) -> str:
    by_tag: dict[str, list[str]] = defaultdict(list)
    for c in all_cards:
        for tag in c.get("tags") or []:
            by_tag[tag].append(c["id"])
    lines = ["| Tag | Templates |", "| --- | --- |"]
    for tag in sorted(by_tag):
        ids = sorted(set(by_tag[tag]))
        preview = ", ".join(f"`{i}`" for i in ids[:6])
        if len(ids) > 6:
            preview += f", … (+{len(ids) - 6})"
        lines.append(f"| `{tag}` | {preview} |")
    return "\n".join(lines)


def render_gates(all_cards: list[dict]) -> str:
    gates = [c for c in all_cards if c.get("gate")]
    if not gates:
        return "_(none)_"
    lines = ["| Id | Category | Domain |", "| --- | --- | --- |"]
    for c in sorted(gates, key=lambda c: c["id"]):
        lines.append(f"| {_link(c)} | {c.get('category') or '—'} | {c.get('domain') or '—'} |")
    return "\n".join(lines)


def render_optionals(all_cards: list[dict]) -> str:
    opts = [c for c in all_cards if c.get("optional")]
    if not opts:
        return "_(none)_"
    lines = ["| Id | Category | Domain |", "| --- | --- | --- |"]
    for c in sorted(opts, key=lambda c: c["id"]):
        lines.append(f"| {_link(c)} | {c.get('category') or '—'} | {c.get('domain') or '—'} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def _card_public_view(fm: dict) -> dict:
    """Frontmatter minus private/agent-generated fields, ready for the UI."""
    view = dict(fm)
    view.pop("_path", None)
    view["path"] = fm["_path"]
    return view


def build_catalog(all_cards: list[dict]) -> dict:
    cards_public = [_card_public_view(c) for c in all_cards]

    def _bucket(field: str) -> dict[str, list[str]]:
        idx: dict[str, list[str]] = defaultdict(list)
        for c in all_cards:
            val = c.get(field)
            if isinstance(val, list):
                for v in val:
                    idx[str(v)].append(c["id"])
            elif val is not None:
                idx[str(val)].append(c["id"])
        return {k: sorted(set(v)) for k, v in idx.items()}

    def _tags_index() -> dict[str, list[str]]:
        idx: dict[str, list[str]] = defaultdict(list)
        for c in all_cards:
            for tag in c.get("tags") or []:
                idx[tag].append(c["id"])
        return {k: sorted(set(v)) for k, v in idx.items()}

    return {
        "version": "0.13.3",
        "total": len(all_cards),
        "cards": cards_public,
        "indexes": {
            "by_artifact_type": _bucket("artifact_type"),
            "by_lifecycle": _bucket("lifecycle"),
            "by_category": _bucket("category"),
            "by_phase": _bucket("phase"),
            "by_domain": _bucket("domain"),
            "by_rollout_stage": _bucket("rollout_stage"),
            "by_autonomy": _bucket("autonomy"),
            "by_role": _bucket("role"),
            "by_mode": _bucket("mode"),
            "by_verticals": _bucket("verticals"),
            "by_tag": _tags_index(),
        },
        "enums": {
            "artifact_type": ARTIFACT_ORDER,
            "lifecycle": ["project", "ops", "both", "none"],
            "rollout_stage": ROLLOUT_STAGES,
            "autonomy": AUTONOMY_LEVELS,
            "ops_domains": OPS_DOMAIN_ORDER,
            "lifecycle_categories": LIFECYCLE_CATEGORY_ORDER,
            "verticals": ["any"] + VERTICAL_ORDER + ["saas", "restaurant"],
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    pairs = load_all()
    all_cards = [fm for _, fm in pairs]

    # Split by lifecycle
    lifecycle_cards = [c for c in all_cards if c.get("lifecycle") in {"project", "both", "none"}]
    ops_cards = [c for c in all_cards if c.get("lifecycle") in {"ops", "both"}]

    by_lc_cat: dict[str, list[dict]] = defaultdict(list)
    for fm in lifecycle_cards:
        by_lc_cat[fm["category"]].append(fm)

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for fm in ops_cards:
        d = fm.get("domain")
        if d:
            by_domain[d].append(fm)

    by_vertical: dict[str, list[dict]] = defaultdict(list)
    for fm in ops_cards:
        for v in fm.get("verticals") or []:
            if v in VERTICAL_TITLE:
                by_vertical[v].append(fm)

    total = len(all_cards)
    n_lc = len(lifecycle_cards)
    n_ops = len(ops_cards)
    n_agents = sum(1 for c in all_cards if c.get("artifact_type") == "agent")
    n_sidecars = sum(1 for c in all_cards if c.get("artifact_type") == "sidecar")
    n_skills = sum(1 for c in all_cards if c.get("artifact_type") == "skill")

    out = []
    out.append("# Agent Templates — Master Index")
    out.append("")
    out.append(
        f"Catalogue of **{total} cards** across two independent axes: "
        f"**{n_lc} project-lifecycle cards** (phases 0-5 + standalone finance) and "
        f"**{n_ops} business-operations cards** (7 domains × 4 rollout stages × 3 autonomy levels). "
        f"By artefact: **{n_agents} agents · {n_sidecars} sidecars · {n_skills} skills**."
    )
    out.append("")
    out.append("Every card carries YAML frontmatter (see [`_schema.md`](_schema.md)). Regenerate this index and the machine-readable [`catalog.json`](catalog.json) via `scripts/build_agent_templates_index.py`.")
    out.append("")

    out.append("## Contents")
    out.append("")
    out.append("- [Project lifecycle catalogue](#project-lifecycle-catalogue)")
    out.append("- [Business operations catalogue](#business-operations-catalogue)")
    out.append("- [Vertical adapters](#vertical-adapters)")
    out.append("- [Gates](#gates)")
    out.append("- [Optional templates](#optional-templates)")
    out.append("- [Index by role](#index-by-role)")
    out.append("- [Index by tag](#index-by-tag)")
    out.append("")

    # ---- Lifecycle catalogue -------------------------------------------------
    out.append("## Project lifecycle catalogue")
    out.append("")
    out.append("Templates that run through the zero-to-fundraise arc (phases 0-5) plus standalone financial-market cards.")
    out.append("")
    out.append("| Category | Templates | Phase |")
    out.append("| --- | ---: | --- |")
    for cat in LIFECYCLE_CATEGORY_ORDER:
        if cat not in by_lc_cat:
            continue
        phase = by_lc_cat[cat][0].get("phase")
        phase_str = f"Phase {phase}" if phase is not None else "—"
        out.append(f"| {LIFECYCLE_TITLE[cat]} | {len(by_lc_cat[cat])} | {phase_str} |")
    out.append("")

    for cat in LIFECYCLE_CATEGORY_ORDER:
        if cat not in by_lc_cat:
            continue
        out.append(f"### {LIFECYCLE_TITLE[cat]}")
        out.append("")
        out.append(render_lifecycle_table(by_lc_cat[cat]))
        out.append("")

    # ---- Ops catalogue ------------------------------------------------------
    out.append("## Business operations catalogue")
    out.append("")
    out.append("Templates that operate a running business — organised by domain, then plotted on a rollout matrix (rows = rollout stage, columns = autonomy). Icons: 🤖 agent · ⚙️ sidecar · 🧩 skill.")
    out.append("")
    out.append("| Domain | Cards |")
    out.append("| --- | ---: |")
    for d in OPS_DOMAIN_ORDER:
        if d not in by_domain:
            continue
        out.append(f"| [{OPS_DOMAIN_TITLE[d]}](#{OPS_DOMAIN_TITLE[d].lower().replace(' ', '-')}) | {len(by_domain[d])} |")
    out.append("")

    for d in OPS_DOMAIN_ORDER:
        if d not in by_domain:
            continue
        out.append(f"### {OPS_DOMAIN_TITLE[d]}")
        out.append("")
        # Filter out vertical cards from the domain view (they live in their own section)
        domain_only = [c for c in by_domain[d] if not (set(c.get("verticals") or []) & set(VERTICAL_ORDER))]
        out.append(render_ops_matrix(domain_only))
        out.append("")
        out.append("<details><summary>Full list</summary>")
        out.append("")
        out.append(render_ops_table(domain_only))
        out.append("")
        out.append("</details>")
        out.append("")

    # ---- Verticals ----------------------------------------------------------
    out.append("## Vertical adapters")
    out.append("")
    out.append("Cards tuned to a specific vertical. They complement the domain-agnostic ops catalogue above — e.g. a real-estate agency uses generic `contact_enrichment` plus its own `property_dossier`.")
    out.append("")
    for v in VERTICAL_ORDER:
        if v not in by_vertical:
            continue
        out.append(f"### {VERTICAL_TITLE[v]}")
        out.append("")
        out.append(render_ops_table(by_vertical[v]))
        out.append("")

    # ---- Cross-cutting indexes ---------------------------------------------
    out.append("## Gates")
    out.append("")
    out.append(render_gates(all_cards))
    out.append("")

    out.append("## Optional templates")
    out.append("")
    out.append(render_optionals(all_cards))
    out.append("")

    out.append("## Index by role")
    out.append("")
    out.append(render_role_index(all_cards))
    out.append("")

    out.append("## Index by tag")
    out.append("")
    out.append(render_tag_index(all_cards))
    out.append("")

    README.write_text("\n".join(out), encoding="utf-8")
    catalog = build_catalog(all_cards)
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=False), encoding="utf-8")

    print(
        f"wrote {README.name} + {CATALOG.name} — {total} cards "
        f"({n_lc} lifecycle + {n_ops} ops; {n_agents} agents + {n_sidecars} sidecars + {n_skills} skills)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
