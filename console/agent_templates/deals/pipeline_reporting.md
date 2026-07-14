---
id: pipeline_reporting
name: pipeline_reporting
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
tools: [read_crm, post_slack]
tags: [pipeline, reporting, dashboard]
gate: false
optional: false
---

# pipeline_reporting

## Identity

```yaml
sidecars:
  - name: pipeline_reporting
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Nightly rollup: pipeline snapshot, stage velocity, coverage, ageing — pushed to dashboards and Slack digest.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `post_slack` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: CRM + activity.
- **Writes**: Dashboard tables + Slack digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
