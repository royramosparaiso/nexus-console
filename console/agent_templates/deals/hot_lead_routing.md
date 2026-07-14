---
id: hot_lead_routing
name: hot_lead_routing
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [read_crm, read_availability]
tags: [routing, assignment, sla]
gate: false
optional: false
---

# hot_lead_routing

## Identity

```yaml
sidecars:
  - name: hot_lead_routing
    role: connector
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Routes hot leads to the right AE based on territory, capacity, ICP fit — SLAs enforced.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_availability` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Classified reply + AE availability.
- **Writes**: Assignment + calendar invite..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
