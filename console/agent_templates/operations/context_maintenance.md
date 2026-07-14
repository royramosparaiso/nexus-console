---
id: context_maintenance
name: context_maintenance
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [vector_db, embed_api]
tags: [context, brain, index]
gate: false
optional: false
---

# context_maintenance

## Identity

```yaml
sidecars:
  - name: context_maintenance
    role: worker
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Keeps the company brain fresh: refreshes indexed docs, dedups, expires stale entries, rebuilds embeddings.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `vector_db` | provider-specific | vendor | maybe |
| `embed_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Doc corpus + last-refresh watermarks.
- **Writes**: Refreshed index..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
