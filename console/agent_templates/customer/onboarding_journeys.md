---
id: onboarding_journeys
name: onboarding_journeys
artifact_type: sidecar
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [email, in_app_messaging]
tags: [onboarding, lifecycle]
gate: false
optional: false
---

# onboarding_journeys

## Identity

```yaml
sidecars:
  - name: onboarding_journeys
    role: worker
    mode: event-driven
    produces: side_effect
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Runs personalised onboarding: sequences, in-app nudges, milestone check-ins based on plan + persona.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `email` | provider-specific | vendor | maybe |
| `in_app_messaging` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Onboarding events.
- **Writes**: Sequences + in-app nudges..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
