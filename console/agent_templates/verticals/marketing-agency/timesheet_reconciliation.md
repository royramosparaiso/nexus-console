---
id: timesheet_reconciliation
name: timesheet_reconciliation
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [marketing-agency]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [timesheet_api, read_budget]
tags: [timesheets, billing, agency]
gate: false
optional: false
---

# timesheet_reconciliation

## Identity

```yaml
sidecars:
  - name: timesheet_reconciliation
    role: worker
    mode: scheduled
    produces: side_effect
    domain: marketing
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Rolls up team timesheets vs budgets per client; flags overruns before month-end.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `timesheet_api` | provider-specific | vendor | maybe |
| `read_budget` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Timesheets + budgets.
- **Writes**: Reconciliation table..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
