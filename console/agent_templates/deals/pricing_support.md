---
id: pricing_support
name: pricing_support
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [pricing_floor, read_crm]
tags: [pricing, quote]
gate: false
optional: false
---

# pricing_support

## Identity

```yaml
agents:
  - name: pricing_support
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Answers deal-level pricing questions: recommended tier, packaging, discount if any, guardrails vs pricing floor.

## Inspiration

Derived from the Business Operations rollout planner — Pricing Support cell in the deals × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `pricing_floor` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal + pricing model.
- **Writes**: Pricing recommendation..
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

- **System**: "You run the Pricing Support job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
