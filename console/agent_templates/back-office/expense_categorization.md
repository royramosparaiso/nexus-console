---
id: expense_categorization
name: expense_categorization
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 3
verticals: [any]
role: classifier
mode: scheduled
depends_on: []
produces: side_effect
tools: [banking_api, read_ledger]
tags: [expense, accounting]
gate: false
optional: false
---

# expense_categorization

## Identity

```yaml
sidecars:
  - name: expense_categorization
    role: classifier
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Classifies bank + card transactions into chart of accounts; flags unknowns for human review.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `banking_api` | provider-specific | vendor | maybe |
| `read_ledger` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Transactions.
- **Writes**: Categorised ledger..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
