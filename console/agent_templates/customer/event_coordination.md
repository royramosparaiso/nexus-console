---
id: event_coordination
name: event_coordination
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: coordinator
mode: single-shot
depends_on: []
produces: markdown_report
tools: [calendar_api, email]
tags: [events, customer]
gate: false
optional: false
---

# event_coordination

## Identity

```yaml
agents:
  - name: event_coordination
    role: coordinator
    mode: single-shot
    produces: markdown_report
    domain: customer
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Coordinates customer events end-to-end — invites, agenda, RSVPs, dinner reservations, follow-ups.

## Inspiration

Derived from the Business Operations rollout planner — Event Coordination cell in the customer × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `calendar_api` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Event brief + guest list.
- **Writes**: Coordination plan + comms..
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

- **System**: "You run the Event Coordination job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
