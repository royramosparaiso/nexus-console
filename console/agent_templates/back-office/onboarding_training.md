---
id: onboarding_training
name: onboarding_training
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: markdown_report
tools: [policy_pack, read_role_scorecard]
tags: [onboarding, hr, training]
gate: false
optional: false
---

# onboarding_training

## Identity

```yaml
agents:
  - name: onboarding_training
    role: writer
    mode: event-driven
    produces: markdown_report
    domain: back-office
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Personalises new-hire onboarding and training plans by role and function; tracks completion.

## Inspiration

Derived from the Business Operations rollout planner — Onboarding & Training cell in the back-office × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `policy_pack` | provider-specific | vendor | maybe |
| `read_role_scorecard` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Role + team.
- **Writes**: Onboarding plan + checklists..
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

- **System**: "You run the Onboarding & Training job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
