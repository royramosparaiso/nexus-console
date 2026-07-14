---
id: calendar_management
name: calendar_management
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [calendar_api]
tags: [calendar, eaa]
gate: false
optional: false
---

# calendar_management

## Identity

```yaml
sidecars:
  - name: calendar_management
    role: worker
    mode: event-driven
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Manages exec calendars: batches meetings, protects deep-work blocks, reschedules conflicts.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `calendar_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Calendar + priorities.
- **Writes**: Reshuffles + confirmations..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
