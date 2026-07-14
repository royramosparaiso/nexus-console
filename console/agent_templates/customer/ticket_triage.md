---
id: ticket_triage
name: ticket_triage
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 3
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: structured_json
tools: [helpdesk_api]
tags: [ticket, triage, cx]
gate: false
optional: false
---

# ticket_triage

## Identity

```yaml
agents:
  - name: ticket_triage
    role: classifier
    mode: event-driven
    produces: structured_json
    domain: customer
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Classifies inbound tickets: intent, urgency, product area, sentiment, PII. Suggests owner and SLA.

## Inspiration

Derived from the Business Operations rollout planner — Ticket Triage cell in the customer × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `helpdesk_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ticket text + customer.
- **Writes**: Classification + routing suggestion..
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

- **System**: "You run the Ticket Triage job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
