---
id: escalations
name: escalations
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: coordinator
mode: event-driven
depends_on: []
produces: markdown_report
tools: [helpdesk_api, read_crm]
tags: [escalation, cx]
gate: false
optional: false
---

# escalations

## Identity

```yaml
agents:
  - name: escalations
    role: coordinator
    mode: event-driven
    produces: markdown_report
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Detects escalation-worthy tickets and drafts an escalation packet + comms to internal owners and customer.

## Inspiration

Derived from the Business Operations rollout planner — Escalations cell in the customer × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `helpdesk_api` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ticket history + account.
- **Writes**: Escalation packet..
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

- **System**: "You run the Escalations job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
