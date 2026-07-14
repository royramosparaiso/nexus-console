#!/usr/bin/env python3
"""Rebuild console/agent_templates/README.md from frontmatter of every card.

Reads every *.md under console/agent_templates/**, parses YAML frontmatter,
and emits a master index grouped by (category, phase) with fast lookup tables
by phase, step, role, mode, tag.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "console" / "agent_templates"
OUT = ROOT / "README.md"

CATEGORY_ORDER = [
    "intake",
    "market-research",
    "mvs",
    "validation",
    "scaling",
    "investor-deliverable",
    "finance",
]

CATEGORY_TITLE = {
    "intake": "Phase 0 · Intake",
    "market-research": "Phase 1 · Market research",
    "mvs": "Phase 2 · Minimal viable setup",
    "validation": "Phase 3 · Market validation",
    "scaling": "Phase 4 · Post-gate scaling",
    "investor-deliverable": "Phase 5 · Investor deliverable",
    "finance": "Standalone · Financial markets (TradingAgents / OpenBB inspired)",
}

REQUIRED_FIELDS = {
    "id", "name", "category", "role", "mode",
    "depends_on", "produces", "tools", "tags", "gate", "optional",
}


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
        out.append((path, fm))
    return out


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


def render_category_table(cards: list[dict]) -> str:
    lines = [
        "| Step | Id | Role | Mode | Produces | Flags |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    cards = sorted(cards, key=lambda c: (c.get("step") if c.get("step") is not None else 999, c["id"]))
    for c in cards:
        lines.append(
            f"| {_fmt_step(c)} "
            f"| [`{c['id']}`]({c['category']}/{c['id']}.md) "
            f"| {c.get('role', '—')} "
            f"| {c.get('mode', '—')} "
            f"| {c.get('produces', '—')} "
            f"| {_fmt_flags(c)} |"
        )
    return "\n".join(lines)


def render_tag_index(all_cards: list[dict]) -> str:
    by_tag: dict[str, list[str]] = defaultdict(list)
    for c in all_cards:
        for tag in c.get("tags") or []:
            by_tag[tag].append(c["id"])
    lines = ["| Tag | Templates |", "| --- | --- |"]
    for tag in sorted(by_tag):
        ids = sorted(set(by_tag[tag]))
        lines.append(f"| `{tag}` | {', '.join(f'`{i}`' for i in ids)} |")
    return "\n".join(lines)


def render_role_index(all_cards: list[dict]) -> str:
    by_role: dict[str, list[str]] = defaultdict(list)
    for c in all_cards:
        by_role[c.get("role", "—")].append(c["id"])
    lines = ["| Role | Count | Templates |", "| --- | ---: | --- |"]
    for role in sorted(by_role):
        ids = sorted(set(by_role[role]))
        lines.append(f"| `{role}` | {len(ids)} | {', '.join(f'`{i}`' for i in ids)} |")
    return "\n".join(lines)


def render_gates(all_cards: list[dict]) -> str:
    gates = [c for c in all_cards if c.get("gate")]
    if not gates:
        return "_(none)_"
    lines = ["| Step | Id | Category |", "| ---: | --- | --- |"]
    for c in sorted(gates, key=lambda c: c.get("step") or 999):
        lines.append(f"| {_fmt_step(c)} | [`{c['id']}`]({c['category']}/{c['id']}.md) | {c['category']} |")
    return "\n".join(lines)


def render_optionals(all_cards: list[dict]) -> str:
    opts = [c for c in all_cards if c.get("optional")]
    if not opts:
        return "_(none)_"
    lines = ["| Step | Id | Category |", "| ---: | --- | --- |"]
    for c in sorted(opts, key=lambda c: c.get("step") or 999):
        lines.append(f"| {_fmt_step(c)} | [`{c['id']}`]({c['category']}/{c['id']}.md) | {c['category']} |")
    return "\n".join(lines)


def main() -> int:
    pairs = load_all()
    all_cards = [fm for _, fm in pairs]

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for fm in all_cards:
        by_cat[fm["category"]].append(fm)

    total = len(all_cards)
    total_pipeline = sum(1 for c in all_cards if c["category"] != "finance")
    total_finance = sum(1 for c in all_cards if c["category"] == "finance")

    out = []
    out.append("# Agent Templates — Master Index")
    out.append("")
    out.append(
        f"Catalog of **{total} agent cards** — {total_pipeline} pipeline templates "
        f"(phases 0-5, one per skill in the project-analysis pipeline) plus "
        f"{total_finance} standalone financial-market templates."
    )
    out.append("")
    out.append("Every card carries YAML frontmatter (see [`_schema.md`](_schema.md)) so the Agent Factory can query, filter and auto-order runs from a single field set. Add a new card: drop a `.md` file under the matching category folder, populate the frontmatter, then rerun `scripts/build_agent_templates_index.py` to refresh this page.")
    out.append("")
    out.append("## Contents")
    out.append("")
    out.append("- [Overview by category](#overview-by-category)")
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        anchor = CATEGORY_TITLE[cat].lower().replace(" · ", "--").replace(" ", "-").replace("(", "").replace(")", "").replace("/", "").replace(".", "")
        out.append(f"  - [{CATEGORY_TITLE[cat]}](#{anchor})")
    out.append("- [Gates](#gates)")
    out.append("- [Optional templates](#optional-templates)")
    out.append("- [Index by role](#index-by-role)")
    out.append("- [Index by tag](#index-by-tag)")
    out.append("")

    out.append("## Overview by category")
    out.append("")
    out.append("| Category | Templates | Phase |")
    out.append("| --- | ---: | --- |")
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        phase = by_cat[cat][0].get("phase")
        phase_str = f"Phase {phase}" if phase is not None else "—"
        out.append(f"| [{CATEGORY_TITLE[cat]}](#{CATEGORY_TITLE[cat].lower().replace(' · ', '--').replace(' ', '-').replace('(', '').replace(')', '').replace('/', '').replace('.', '')}) | {len(by_cat[cat])} | {phase_str} |")
    out.append("")

    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        out.append(f"## {CATEGORY_TITLE[cat]}")
        out.append("")
        out.append(render_category_table(by_cat[cat]))
        out.append("")

    out.append("## Gates")
    out.append("")
    out.append("Templates that emit a binary or thresholded decision. Downstream templates must refuse to run until the upstream gate returns PASS.")
    out.append("")
    out.append(render_gates(all_cards))
    out.append("")

    out.append("## Optional templates")
    out.append("")
    out.append("Templates the coordinator skips unless upstream logic activates them (e.g. mobile-app spec only if step 26 recommends mobile, valuation and fundraising only if the founder chooses to raise).")
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

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT} — {total} cards ({total_pipeline} pipeline + {total_finance} finance)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
