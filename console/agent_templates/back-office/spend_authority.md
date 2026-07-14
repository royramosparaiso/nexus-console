---
id: spend_authority
name: spend_authority
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: reviewer
mode: single-shot
depends_on: []
produces: decision
tools: [read_budget, policy_check]
tags: [spend, approval, founder-led]
gate: false
optional: false
---

# spend_authority

## Identity

```yaml
agents:
  - name: spend_authority
    role: reviewer
    mode: single-shot
    produces: decision
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led. Approves or holds spend requests against policy + budget.

## Inspiration

Derived from the Business Operations rollout planner — Spend Authority cell in the back-office × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_budget` | provider-specific | vendor | maybe |
| `policy_check` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Spend request + budget.
- **Writes**: Decision..
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

- **System**: "You run the Spend Authority job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
