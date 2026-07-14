#!/usr/bin/env python3
"""Materialise the ops catalog specs into individual markdown cards.

Each card gets:
- Full v0.13.0 frontmatter (with ops axis populated)
- Identity block
- Purpose paragraph
- Wiring section (reads / writes)
- Trigger + Side effects (sidecars) / Inputs + Outputs (skills) / rest for agents

Cards are deterministic — running this twice produces the same bytes.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `import scripts.ops_catalog_spec` when run from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from scripts.ops_catalog_spec import SALES, DEALS
from scripts.ops_catalog_spec2 import (
    MARKETING, OPERATIONS, INTELLIGENCE, CUSTOMER, BACK_OFFICE,
    REAL_ESTATE, MARKETING_AGENCY, NIGHTCLUB,
)

TEMPLATES = ROOT / "console" / "agent_templates"

DOMAIN_DIRS = {
    "sales": TEMPLATES / "sales",
    "deals": TEMPLATES / "deals",
    "marketing": TEMPLATES / "marketing",
    "operations": TEMPLATES / "operations",
    "intelligence": TEMPLATES / "intelligence",
    "customer": TEMPLATES / "customer",
    "back-office": TEMPLATES / "back-office",
    "real-estate": TEMPLATES / "verticals" / "real-estate",
    "marketing-agency": TEMPLATES / "verticals" / "marketing-agency",
    "nightclub": TEMPLATES / "verticals" / "nightclub",
}

# Where a domain-domain-agnostic skill belongs
SKILL_DIR = TEMPLATES / "skills"


def _yaml_dump(fm: dict) -> str:
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


def _domain_for_spec(spec: dict, default_domain: str) -> str:
    """Return the ops domain string for the card."""
    if "vertical" in spec:
        # Vertical cards still belong to a functional domain (default) but sit
        # under the verticals directory.
        return default_domain
    return default_domain


def _category_for(spec: dict, default_domain: str) -> str:
    if "vertical" in spec:
        return "verticals"
    return default_domain


def _directory_for(spec: dict, default_domain: str) -> Path:
    if "vertical" in spec:
        return DOMAIN_DIRS[spec["vertical"]]
    if spec.get("artifact") == "skill":
        return SKILL_DIR
    return DOMAIN_DIRS[default_domain]


def _verticals(spec: dict) -> list[str]:
    if "vertical" in spec:
        return [spec["vertical"]]
    return ["any"]


def _build_frontmatter(spec: dict, default_domain: str) -> dict:
    artifact = spec["artifact"]
    fm = {
        "id": spec["id"],
        "name": spec["id"],
        "artifact_type": artifact,
        "lifecycle": "ops",
        "category": _category_for(spec, default_domain),
        "phase": None,
        "step": None,
        "domain": default_domain,
        "rollout_stage": spec["stage"],
        "autonomy": spec["autonomy"],
        "maturity": spec["maturity"],
        "verticals": _verticals(spec),
        "role": spec.get("role"),
        "mode": spec.get("mode"),
        "depends_on": spec.get("depends_on", []),
        "produces": spec["produces"],
        "tools": spec["tools"],
        "tags": spec["tags"],
        "gate": bool(spec.get("gate", False)),
        "optional": bool(spec.get("optional", False)),
    }
    return fm


def _body_agent(spec: dict, fm: dict) -> str:
    tools_rows = "\n".join(f"| `{t}` | provider-specific | vendor | maybe |" for t in spec["tools"])
    return f"""# {spec["id"]}

## Identity

```yaml
agents:
  - name: {spec["id"]}
    role: {fm["role"] or "worker"}
    mode: {fm["mode"] or "single-shot"}
    produces: {fm["produces"]}
    domain: {fm["domain"]}
    rollout_stage: {fm["rollout_stage"]}
    autonomy: {fm["autonomy"]}
```

## Purpose

{spec["purpose"]}

## Inspiration

Derived from the Business Operations rollout planner — {spec["title"]} cell in the {fm["domain"]} × {fm["rollout_stage"]} × {fm["autonomy"]} matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
{tools_rows}

## Wiring

- **Reads**: {spec["reads"]}.
- **Writes**: {spec["writes"]}.
- **Upstream**: signals or artefacts from foundation-stage cards in the same domain.
- **Downstream**: consumed by orchestration-stage cards or the human operator.

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the {spec["title"]} job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
"""


def _body_sidecar(spec: dict, fm: dict) -> str:
    trigger = {
        "streaming": "consumes a live event stream (WebSocket / SSE / message bus)",
        "scheduled": "runs on a fixed cron cadence",
        "event-driven": "reacts to webhooks or queue messages",
        "single-shot": "invoked on demand",
    }.get(fm["mode"] or "event-driven", "event-driven")
    tools_rows = "\n".join(f"| `{t}` | provider-specific | vendor | maybe |" for t in spec["tools"])
    return f"""# {spec["id"]}

## Identity

```yaml
sidecars:
  - name: {spec["id"]}
    role: {fm["role"] or "worker"}
    mode: {fm["mode"] or "event-driven"}
    produces: {fm["produces"]}
    domain: {fm["domain"]}
    rollout_stage: {fm["rollout_stage"]}
    autonomy: {fm["autonomy"]}
```

## Purpose

{spec["purpose"]}

## Trigger

Sidecar {trigger}.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
{tools_rows}

## Wiring

- **Reads**: {spec["reads"]}.
- **Writes**: {spec["writes"]}.

## Side effects

- Emits {fm["produces"]} to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
"""


def _body_skill(spec: dict, fm: dict) -> str:
    tools_rows = "\n".join(f"| `{t}` | provider-specific | vendor | maybe |" for t in spec["tools"])
    return f"""# {spec["id"]}

## Identity

```yaml
skills:
  - name: {spec["id"]}
    kind: skill
    produces: {fm["produces"]}
    domain: {fm["domain"]}
```

## Purpose

{spec["purpose"]}

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
{tools_rows}

## Inputs

{spec["reads"]}.

## Outputs

{spec["writes"]}.

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
"""


def _write_card(spec: dict, default_domain: str) -> Path:
    fm = _build_frontmatter(spec, default_domain)
    if spec["artifact"] == "agent":
        body = _body_agent(spec, fm)
    elif spec["artifact"] == "sidecar":
        body = _body_sidecar(spec, fm)
    elif spec["artifact"] == "skill":
        body = _body_skill(spec, fm)
    else:
        raise ValueError(f"unknown artifact: {spec['artifact']}")

    directory = _directory_for(spec, default_domain)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{spec['id']}.md"
    text = f"---\n{_yaml_dump(fm)}---\n\n{body}"
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    domain_lists = [
        ("sales", SALES),
        ("deals", DEALS),
        ("marketing", MARKETING),
        ("operations", OPERATIONS),
        ("intelligence", INTELLIGENCE),
        ("customer", CUSTOMER),
        ("back-office", BACK_OFFICE),
    ]

    written = 0
    for default_domain, specs in domain_lists:
        for spec in specs:
            _write_card(spec, default_domain)
            written += 1

    # Verticals: default_domain matches spec's functional domain.
    vertical_lists = [
        ("sales", REAL_ESTATE),   # RE cards mostly capture/generate sales/deals ops
        ("marketing", MARKETING_AGENCY),
        ("operations", NIGHTCLUB),
    ]
    for default_domain, specs in vertical_lists:
        for spec in specs:
            _write_card(spec, default_domain)
            written += 1

    print(f"wrote {written} ops cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
