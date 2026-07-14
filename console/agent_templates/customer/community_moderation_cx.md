---
id: community_moderation_cx
name: community_moderation_cx
artifact_type: sidecar
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: side_effect
tools: [discord_api, slack_api]
tags: [community, moderation, cx]
gate: false
optional: false
---

# community_moderation_cx

## Identity

```yaml
sidecars:
  - name: community_moderation_cx
    role: classifier
    mode: event-driven
    produces: side_effect
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches customer communities; flags issues, drafts responses, escalates edge cases to CX humans.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `discord_api` | provider-specific | vendor | maybe |
| `slack_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Community stream.
- **Writes**: Moderation actions + drafts..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
