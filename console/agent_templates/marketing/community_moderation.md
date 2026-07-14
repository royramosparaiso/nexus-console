---
id: community_moderation
name: community_moderation
artifact_type: sidecar
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: side_effect
tools: [discord_api, slack_api]
tags: [community, moderation]
gate: false
optional: false
---

# community_moderation

## Identity

```yaml
sidecars:
  - name: community_moderation
    role: classifier
    mode: event-driven
    produces: side_effect
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches Discord/Slack/forum channels: flags spam and toxicity, drafts responses on FAQ questions, escalates edge cases.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `discord_api` | provider-specific | vendor | maybe |
| `slack_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Community message stream.
- **Writes**: Moderation actions + response drafts..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
