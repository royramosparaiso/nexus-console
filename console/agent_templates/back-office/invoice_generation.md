---
id: invoice_generation
name: invoice_generation
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: pdf
tools: [read_crm, read_pm_board, write_pdf]
tags: [invoice, billing]
gate: false
optional: false
---

# invoice_generation

## Identity

```yaml
agents:
  - name: invoice_generation
    role: writer
    mode: event-driven
    produces: pdf
    domain: back-office
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Generates invoices from CRM/PM events, delivers to the customer portal + email, syncs to ledger.

## Inspiration

Derived from the Business Operations rollout planner — Invoice Generation cell in the back-office × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_pm_board` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal + milestone events.
- **Writes**: Invoice PDFs + ledger entries..
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

- **System**: "You run the Invoice Generation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
