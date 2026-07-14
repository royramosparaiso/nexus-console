---
id: deal_room_assembly
name: deal_room_assembly
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
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [docsend_api, notion_api, dock_api]
tags: [deal-room, engagement]
gate: false
optional: false
---

# deal_room_assembly

## Identity

```yaml
sidecars:
  - name: deal_room_assembly
    role: connector
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Provisions a per-deal digital room (DocSend/Notion/Dock) with the right artefacts, tracks buyer engagement, alerts on stalls.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `docsend_api` | provider-specific | vendor | maybe |
| `notion_api` | provider-specific | vendor | maybe |
| `dock_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal record.
- **Writes**: Room provisioned + engagement stream..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
