---
id: cost_usage_tracking
name: cost_usage_tracking
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [provider_usage_api, post_slack]
tags: [cost, usage, finops]
gate: false
optional: false
---

# cost_usage_tracking

## Identity

```yaml
sidecars:
  - name: cost_usage_tracking
    role: worker
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Aggregates per-agent, per-tenant token + tool costs; alerts on budget overruns and pushes weekly cost digest.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `provider_usage_api` | provider-specific | vendor | maybe |
| `post_slack` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Provider usage APIs + tool ledger.
- **Writes**: Cost table + digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
