---
id: send_optimization
name: send_optimization
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_engagement_history, inbox_reputation]
tags: [send-time, throttle, deliverability]
gate: false
optional: false
---

# send_optimization

## Identity

```yaml
sidecars:
  - name: send_optimization
    role: worker
    mode: scheduled
    produces: side_effect
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Optimises send-time per contact using timezone + engagement history and enforces per-inbox rate limits to protect deliverability.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_engagement_history` | provider-specific | vendor | maybe |
| `inbox_reputation` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Contact activity + inbox reputation.
- **Writes**: Send-time overrides on the outbound queue..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
