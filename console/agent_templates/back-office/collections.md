---
id: collections
name: collections
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_ledger, email]
tags: [collections, ar]
gate: false
optional: false
---

# collections

## Identity

```yaml
agents:
  - name: collections
    role: writer
    mode: scheduled
    produces: markdown_report
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Runs the collections cadence: identifies overdue invoices, drafts escalating comms, escalates to human on impasse.

## Inspiration

Derived from the Business Operations rollout planner — Collections cell in the back-office × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_ledger` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: AR ledger.
- **Writes**: Cadence drafts..
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

- **System**: "You run the Collections job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
