---
id: goal_pacing
name: goal_pacing
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_kpis, post_slack]
tags: [pacing, kpi]
gate: false
optional: false
---

# goal_pacing

## Identity

```yaml
sidecars:
  - name: goal_pacing
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Rolls up KPI attainment vs plan; sends weekly pacing digest with lagging metrics highlighted.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_kpis` | provider-specific | vendor | maybe |
| `post_slack` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: KPI streams.
- **Writes**: Pacing digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
