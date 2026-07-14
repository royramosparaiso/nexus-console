---
id: data_migration
name: data_migration
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [schema_diff, etl_runner]
tags: [migration, etl]
gate: false
optional: false
---

# data_migration

## Identity

```yaml
sidecars:
  - name: data_migration
    role: worker
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Orchestrates data-migration jobs between source and destination systems; produces mapping doc, diff report, rollback plan.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `schema_diff` | provider-specific | vendor | maybe |
| `etl_runner` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Source + target schemas.
- **Writes**: Migration report..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
