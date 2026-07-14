---
id: incident_book
name: incident_book
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [nightclub]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [door_scanner_api, vault_api]
tags: [incident, safety, nightclub]
gate: false
optional: false
---

# incident_book

## Identity

```yaml
sidecars:
  - name: incident_book
    role: worker
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Captures door + floor incidents: refusals, ejections, medical, damage — with time, staff, evidence links.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `door_scanner_api` | provider-specific | vendor | maybe |
| `vault_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Radio + door log intake.
- **Writes**: Incident records + weekly digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
