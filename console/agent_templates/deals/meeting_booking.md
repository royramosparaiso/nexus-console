---
id: meeting_booking
name: meeting_booking
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
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [chili_piper, calendly, google_calendar]
tags: [scheduling, meeting]
gate: false
optional: false
---

# meeting_booking

## Identity

```yaml
sidecars:
  - name: meeting_booking
    role: connector
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Handles back-and-forth to book meetings with qualified leads across time zones — proposes slots, holds and confirms.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `chili_piper` | provider-specific | vendor | maybe |
| `calendly` | provider-specific | vendor | maybe |
| `google_calendar` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Qualified lead + AE availability.
- **Writes**: Calendar invite + confirmation email..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
