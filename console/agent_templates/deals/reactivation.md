---
id: reactivation
name: reactivation
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_crm, signal_detection]
tags: [reactivation, closed-lost]
gate: false
optional: false
---

# reactivation

## Identity

```yaml
sidecars:
  - name: reactivation
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Watches closed-lost and cold-open deals for reactivation signals — job change, funding, new decision-maker — and reopens with a tailored touch.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `signal_detection` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Closed-lost + cold-open pool.
- **Writes**: Reactivation touches on the outbound queue..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
