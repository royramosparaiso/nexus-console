---
id: reservation_handling
name: reservation_handling
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [nightclub]
role: writer
mode: event-driven
depends_on: []
produces: markdown_report
tools: [whatsapp_api, instagram_api, reservation_system]
tags: [reservations, nightclub]
gate: false
optional: false
---

# reservation_handling

## Identity

```yaml
agents:
  - name: reservation_handling
    role: writer
    mode: event-driven
    produces: markdown_report
    domain: operations
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Handles reservation inbounds (WhatsApp, DM, email): qualifies party, quotes, confirms, adds to floor plan.

## Inspiration

Derived from the Business Operations rollout planner — Reservation Handling cell in the operations × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `whatsapp_api` | provider-specific | vendor | maybe |
| `instagram_api` | provider-specific | vendor | maybe |
| `reservation_system` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Inbound request.
- **Writes**: Confirmation + floor plan update..
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

- **System**: "You run the Reservation Handling job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
