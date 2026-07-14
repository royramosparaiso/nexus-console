---
id: comment_cta_fulfillment
name: comment_cta_fulfillment
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [instagram_api, linkedin_api, crm_upsert]
tags: [cta, social, inbound]
gate: false
optional: false
---

# comment_cta_fulfillment

## Identity

```yaml
sidecars:
  - name: comment_cta_fulfillment
    role: worker
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

When a prospect drops the CTA keyword on a social post, DMs them the lead magnet and opens a CRM record.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `instagram_api` | provider-specific | vendor | maybe |
| `linkedin_api` | provider-specific | vendor | maybe |
| `crm_upsert` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Social listening stream.
- **Writes**: DM + CRM record..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
