---
id: discounting_concessions
name: discounting_concessions
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, pricing_floor]
tags: [discount, concession, ae-led]
gate: false
optional: false
---

# discounting_concessions

## Identity

```yaml
agents:
  - name: discounting_concessions
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Analyses proposed discount vs deal size, LTV, competitive pressure — recommends approve/counter/hold with rationale.

## Inspiration

Derived from the Business Operations rollout planner — Discounting & Concessions cell in the deals × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `pricing_floor` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal record + pricing floor.
- **Writes**: Discount recommendation..
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

- **System**: "You run the Discounting & Concessions job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
