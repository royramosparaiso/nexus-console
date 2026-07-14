---
id: bar_inventory
name: bar_inventory
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [nightclub]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [pos_api]
tags: [inventory, bar, nightclub]
gate: false
optional: false
---

# bar_inventory

## Identity

```yaml
sidecars:
  - name: bar_inventory
    role: worker
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Reconciles POS pours vs stock counts; flags shrink, low-stock, forecasts reorder points.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `pos_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: POS + stock counts.
- **Writes**: Shrink report + reorder list..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
