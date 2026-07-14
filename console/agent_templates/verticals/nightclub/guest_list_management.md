---
id: guest_list_management
name: guest_list_management
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [nightclub]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [door_scanner_api, crm_upsert]
tags: [guest-list, door, nightclub]
gate: false
optional: false
---

# guest_list_management

## Identity

```yaml
sidecars:
  - name: guest_list_management
    role: worker
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Manages nightly guest lists across sources (social, promoters, VIP): dedup, tier, arrival tracking.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `door_scanner_api` | provider-specific | vendor | maybe |
| `crm_upsert` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: RSVP sources.
- **Writes**: Guest list + tier + status..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
