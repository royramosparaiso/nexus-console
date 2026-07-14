---
id: portal_sync
name: portal_sync
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: connector
mode: scheduled
depends_on: []
produces: side_effect
tools: [portal_api, crm_api, pm_api]
tags: [sync, portal]
gate: false
optional: false
---

# portal_sync

## Identity

```yaml
sidecars:
  - name: portal_sync
    role: connector
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Two-way sync between the client portal and internal systems (CRM, PM tool) so state is never stale.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `portal_api` | provider-specific | vendor | maybe |
| `crm_api` | provider-specific | vendor | maybe |
| `pm_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Portal + internal system.
- **Writes**: Reconciled state on both sides..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
