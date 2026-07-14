---
id: trigger_detection
name: trigger_detection
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: side_effect
tools: [subscribe_signals, classify, route_to_playbook]
tags: [triggers, signals, routing]
gate: false
optional: false
---

# trigger_detection

## Identity

```yaml
sidecars:
  - name: trigger_detection
    role: classifier
    mode: event-driven
    produces: side_effect
    domain: sales
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Detects buying triggers in signal streams (funding, hiring, role change, product launch) and routes them to the right SDR playbook.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `subscribe_signals` | provider-specific | vendor | maybe |
| `classify` | provider-specific | vendor | maybe |
| `route_to_playbook` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Signal stream from social/news mining.
- **Writes**: Trigger events on the sales bus..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
