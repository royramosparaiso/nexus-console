---
id: crm_sync
name: crm_sync
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
role: connector
mode: scheduled
depends_on: []
produces: side_effect
tools: [crm_api, billing_api, pm_api]
tags: [sync, crm, connector]
gate: false
optional: false
---

# crm_sync

## Identity

```yaml
sidecars:
  - name: crm_sync
    role: connector
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Two-way sync between primary CRM and secondary systems (billing, PM, marketing) with idempotent upserts.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `crm_api` | provider-specific | vendor | maybe |
| `billing_api` | provider-specific | vendor | maybe |
| `pm_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: System-of-record deltas.
- **Writes**: Reconciled state..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
