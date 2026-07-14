---
id: email_triage_office
name: email_triage_office
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: side_effect
tools: [gmail_api, outlook_api]
tags: [inbox, exec, triage]
gate: false
optional: false
---

# email_triage_office

## Identity

```yaml
sidecars:
  - name: email_triage_office
    role: classifier
    mode: event-driven
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Classifies exec inbox: urgent / needs-reply / FYI / newsletter / spam; drafts responses on repeatable buckets.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `gmail_api` | provider-specific | vendor | maybe |
| `outlook_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Exec inbox stream.
- **Writes**: Labels + draft responses..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
