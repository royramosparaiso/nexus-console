---
id: revenue_reporting
name: revenue_reporting
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_billing, read_crm, write_pptx]
tags: [revenue, reporting, board]
gate: false
optional: false
---

# revenue_reporting

## Identity

```yaml
sidecars:
  - name: revenue_reporting
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Monthly revenue rollup by product, segment, geo; sends board pack pre-draft.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_billing` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |
| `write_pptx` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Billing + CRM.
- **Writes**: Board pack draft..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
