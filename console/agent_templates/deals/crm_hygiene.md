---
id: crm_hygiene
name: crm_hygiene
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_crm, crm_upsert, ticket_create]
tags: [crm, hygiene, cleanup]
gate: false
optional: false
---

# crm_hygiene

## Identity

```yaml
sidecars:
  - name: crm_hygiene
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Detects stale deals, missing fields, orphaned contacts, duplicate accounts — remediates or opens tickets.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `crm_upsert` | provider-specific | vendor | maybe |
| `ticket_create` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: CRM full scan.
- **Writes**: Field fills, dedup merges, ticket creates..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
