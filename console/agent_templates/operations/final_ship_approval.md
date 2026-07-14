---
id: final_ship_approval
name: final_ship_approval
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: reviewer
mode: single-shot
depends_on: []
produces: decision
tools: [diff]
tags: [approval, gate, operator-led]
gate: false
optional: false
---

# final_ship_approval

## Identity

```yaml
agents:
  - name: final_ship_approval
    role: reviewer
    mode: single-shot
    produces: decision
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Operator-led. Structured go/no-go review of deliverables before client hand-off.

## Inspiration

Derived from the Business Operations rollout planner — Final Ship Approval cell in the operations × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `diff` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deliverable + acceptance criteria.
- **Writes**: Decision + inline notes..
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

- **System**: "You run the Final Ship Approval job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
