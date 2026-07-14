---
id: speed_to_lead
name: speed_to_lead
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [gmail_api, whatsapp_api, calendly]
tags: [speed, response-sla, inbound]
gate: false
optional: false
---

# speed_to_lead

## Identity

```yaml
sidecars:
  - name: speed_to_lead
    role: worker
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Watches inbound signals and responds within 60 seconds — first-touch email or WhatsApp acknowledging and offering a meeting slot.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `gmail_api` | provider-specific | vendor | maybe |
| `whatsapp_api` | provider-specific | vendor | maybe |
| `calendly` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Fresh inbound signal.
- **Writes**: First-touch send + meeting-link..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
