---
id: ugc_pipeline
name: ugc_pipeline
artifact_type: sidecar
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [social_listening, rights_check]
tags: [ugc, content, social-proof]
gate: false
optional: false
---

# ugc_pipeline

## Identity

```yaml
sidecars:
  - name: ugc_pipeline
    role: worker
    mode: event-driven
    produces: side_effect
    domain: marketing
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Collects user-generated content mentions, verifies rights, tags for reuse across social and site.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `social_listening` | provider-specific | vendor | maybe |
| `rights_check` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Social listening + rights DB.
- **Writes**: Approved UGC library..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
