---
id: account_monitoring
name: account_monitoring
artifact_type: sidecar
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [web_search, news_api, linkedin_api]
tags: [monitoring, signals, accounts]
gate: false
optional: false
---

# account_monitoring

## Identity

```yaml
sidecars:
  - name: account_monitoring
    role: worker
    mode: scheduled
    produces: side_effect
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches target accounts for news, filings, hiring, executive moves — surfaces trigger events to the SDR/AE.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `news_api` | provider-specific | vendor | maybe |
| `linkedin_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account list.
- **Writes**: Trigger events..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
