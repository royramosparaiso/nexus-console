---
id: monitoring_alerting
name: monitoring_alerting
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [metrics_api, post_slack]
tags: [monitoring, alerting, sre]
gate: false
optional: false
---

# monitoring_alerting

## Identity

```yaml
sidecars:
  - name: monitoring_alerting
    role: worker
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches agents in production: latency, error rate, cost, output shape. Fires alerts on anomalies.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `metrics_api` | provider-specific | vendor | maybe |
| `post_slack` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Agent metrics stream.
- **Writes**: Alerts on ops channel..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
