---
id: budget_tracking
name: budget_tracking
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_ledger, read_budget]
tags: [budget, burn]
gate: false
optional: false
---

# budget_tracking

## Identity

```yaml
sidecars:
  - name: budget_tracking
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Tracks budget vs actuals per department + project; sends monthly burn digest with variance notes.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_ledger` | provider-specific | vendor | maybe |
| `read_budget` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Budget + actuals.
- **Writes**: Burn digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
