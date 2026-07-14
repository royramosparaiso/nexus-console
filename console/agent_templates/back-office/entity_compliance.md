---
id: entity_compliance
name: entity_compliance
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_registry]
tags: [entity, compliance, founder-led]
gate: false
optional: false
---

# entity_compliance

## Identity

```yaml
agents:
  - name: entity_compliance
    role: analyst
    mode: scheduled
    produces: markdown_report
    domain: back-office
    rollout_stage: 2-capture
    autonomy: human-led
```

## Purpose

Founder-led. Tracks annual filings, board resolutions, corporate books across entities (US, ES, EE).

## Inspiration

Derived from the Business Operations rollout planner — Entity Compliance cell in the back-office × 2-capture × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_registry` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Entity registry + calendars.
- **Writes**: Compliance state + next actions..
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

- **System**: "You run the Entity Compliance job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
