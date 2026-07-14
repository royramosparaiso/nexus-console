---
id: health_scoring
name: health_scoring
artifact_type: sidecar
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 3
verticals: [any]
role: classifier
mode: scheduled
depends_on: []
produces: structured_json
tools: [read_usage, helpdesk_api]
tags: [health, csm, signals]
gate: false
optional: false
---

# health_scoring

## Identity

```yaml
sidecars:
  - name: health_scoring
    role: classifier
    mode: scheduled
    produces: structured_json
    domain: customer
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Rolls usage, sentiment, tickets and NPS into a per-customer health score with drivers and recommended play.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_usage` | provider-specific | vendor | maybe |
| `helpdesk_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Usage + tickets + surveys.
- **Writes**: Health scores..

## Side effects

- Emits structured_json to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
