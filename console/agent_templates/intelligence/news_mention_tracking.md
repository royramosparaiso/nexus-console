---
id: news_mention_tracking
name: news_mention_tracking
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
tools: [news_api, google_alerts]
tags: [news, monitoring, brand]
gate: false
optional: false
---

# news_mention_tracking

## Identity

```yaml
sidecars:
  - name: news_mention_tracking
    role: worker
    mode: scheduled
    produces: side_effect
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches media for mentions of company, competitors, partners; routes noteworthy items to owners.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `news_api` | provider-specific | vendor | maybe |
| `google_alerts` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Watchlist.
- **Writes**: Digest per owner..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
