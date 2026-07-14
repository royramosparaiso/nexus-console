---
id: alert_routing
name: alert_routing
artifact_type: sidecar
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [post_slack, email]
tags: [alerts, routing]
gate: false
optional: false
---

# alert_routing

## Identity

```yaml
sidecars:
  - name: alert_routing
    role: connector
    mode: event-driven
    produces: side_effect
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Routes intelligence alerts to the right owner + channel by topic, account and priority — dedups and rate-limits.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `post_slack` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Alert stream.
- **Writes**: Owner-routed alerts..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
