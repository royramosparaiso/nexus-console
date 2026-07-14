---
id: screening_scheduling
name: screening_scheduling
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [email, calendar_api]
tags: [hiring, screening]
gate: false
optional: false
---

# screening_scheduling

## Identity

```yaml
sidecars:
  - name: screening_scheduling
    role: connector
    mode: event-driven
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Runs first-round screens (short-answer questionnaires) and books interviews across the panel.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `email` | provider-specific | vendor | maybe |
| `calendar_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Candidate pipeline.
- **Writes**: Screen results + calendar invites..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
