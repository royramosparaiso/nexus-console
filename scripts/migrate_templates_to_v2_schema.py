#!/usr/bin/env python3
"""One-shot migration: add v0.13.0 fields to existing 46 cards.

Adds `artifact_type`, `lifecycle`, `domain`, `rollout_stage`, `autonomy`,
`maturity`, `verticals` to every existing frontmatter block. Preserves
key order roughly — the tests don't care about YAML key order, only
about field presence.

For every existing card:
- artifact_type = "agent"           (all 46 existing cards are agents)
- lifecycle = "project" for phases 0-5; "none" for finance
- domain / rollout_stage / autonomy / maturity: null
- verticals = ["any"]
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "console" / "agent_templates"

FIN_CATEGORY = "finance"


def _yaml_dump_ordered(fm: dict) -> str:
    # Preserve a canonical key order so diffs are readable.
    order = [
        "id", "name",
        "artifact_type", "lifecycle",
        "category", "phase", "step",
        "domain", "rollout_stage", "autonomy", "maturity",
        "verticals",
        "role", "mode", "depends_on", "produces",
        "tools", "tags", "gate", "optional",
    ]
    ordered = {}
    for key in order:
        if key in fm:
            ordered[key] = fm[key]
    for key, value in fm.items():
        if key not in ordered:
            ordered[key] = value
    return yaml.dump(ordered, sort_keys=False, allow_unicode=True, default_flow_style=None).rstrip() + "\n"


def migrate_card(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return False
    fm = yaml.safe_load(m.group(1))
    if not isinstance(fm, dict):
        return False

    # Skip if already migrated
    if "artifact_type" in fm and "lifecycle" in fm:
        return False

    fm["artifact_type"] = "agent"

    category = fm.get("category")
    if category == FIN_CATEGORY:
        fm["lifecycle"] = "none"
    else:
        fm["lifecycle"] = "project"

    # Ops fields default to null for these 46 pipeline/finance agents
    fm.setdefault("domain", None)
    fm.setdefault("rollout_stage", None)
    fm.setdefault("autonomy", None)
    fm.setdefault("maturity", None)
    fm.setdefault("verticals", ["any"])

    body = text[m.end():]
    new_fm = _yaml_dump_ordered(fm)
    path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    total = 0
    for path in sorted(ROOT.rglob("*.md")):
        if path.name in {"README.md", "_schema.md"}:
            continue
        total += 1
        if migrate_card(path):
            changed += 1
    print(f"migrated {changed} of {total} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
