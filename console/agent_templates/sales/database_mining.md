---
id: database_mining
name: database_mining
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: enriched_record
tools: [fetch_url, wide_browse, crm_upsert]
tags: [mining, sync, database]
gate: false
optional: false
---

# database_mining

## Identity

```yaml
sidecars:
  - name: database_mining
    role: worker
    mode: scheduled
    produces: enriched_record
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Runs scheduled sweeps against directories (Crunchbase, LinkedIn, industry lists) to keep the target-account database fresh.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fetch_url` | provider-specific | vendor | maybe |
| `wide_browse` | provider-specific | vendor | maybe |
| `crm_upsert` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Source connector list + last sync watermark.
- **Writes**: New / updated accounts into the CRM staging table..

## Side effects

- Emits enriched_record to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
