---
id: inbox_triage
name: inbox_triage
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
role: classifier
mode: event-driven
depends_on: []
produces: side_effect
tools: [gmail_api, outlook_api]
tags: [inbox, triage, shared-inbox]
gate: false
optional: false
---

# inbox_triage

## Identity

```yaml
sidecars:
  - name: inbox_triage
    role: classifier
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Deduplicates inbound emails across shared mailboxes, labels by intent, routes to the owning queue.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `gmail_api` | provider-specific | vendor | maybe |
| `outlook_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Shared inbox stream.
- **Writes**: Labels + routing on inbox platform..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
