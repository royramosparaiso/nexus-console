---
id: churn_prediction
name: churn_prediction
artifact_type: sidecar
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: classifier
mode: scheduled
depends_on: []
produces: structured_json
tools: [read_usage, helpdesk_api]
tags: [churn, prediction]
gate: false
optional: false
---

# churn_prediction

## Identity

```yaml
sidecars:
  - name: churn_prediction
    role: classifier
    mode: scheduled
    produces: structured_json
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Predicts churn risk 90 days out using usage, tickets, comms signals; explains top drivers per account.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_usage` | provider-specific | vendor | maybe |
| `helpdesk_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Health signals.
- **Writes**: Churn risk table..

## Side effects

- Emits structured_json to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
