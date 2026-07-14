---
id: hr_policy_assistant
name: hr_policy_assistant
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: markdown_report
tools: [policy_pack, letter_templates]
tags: [hr, policy]
gate: false
optional: false
---

# hr_policy_assistant

## Identity

```yaml
agents:
  - name: hr_policy_assistant
    role: writer
    mode: event-driven
    produces: markdown_report
    domain: back-office
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Answers employee questions against policy pack, generates offer letters, PIPs and separation letters (draft only).

## Inspiration

Derived from the Business Operations rollout planner — HR & Policy Assistant cell in the back-office × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `policy_pack` | provider-specific | vendor | maybe |
| `letter_templates` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Policy pack + request.
- **Writes**: Response or draft doc..
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

- **System**: "You run the HR & Policy Assistant job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
