---
id: payment_tracking
name: payment_tracking
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [banking_api, stripe_api, read_ledger]
tags: [payments, reconciliation]
gate: false
optional: false
---

# payment_tracking

## Identity

```yaml
sidecars:
  - name: payment_tracking
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Reconciles bank + processor + invoice states; flags mismatches for AR/AP.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `banking_api` | provider-specific | vendor | maybe |
| `stripe_api` | provider-specific | vendor | maybe |
| `read_ledger` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Bank + processor + AR ledger.
- **Writes**: Reconciliation report + tickets..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
