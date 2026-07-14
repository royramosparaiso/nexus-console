---
id: social_mining
name: social_mining
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: enriched_record
tools: [fetch_url, linkedin_api, x_api]
tags: [social, signals, linkedin]
gate: false
optional: false
---

# social_mining

## Identity

```yaml
sidecars:
  - name: social_mining
    role: worker
    mode: scheduled
    produces: enriched_record
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Watches social platforms (LinkedIn, X, Instagram) for role changes, hiring signals, funding announcements matching the ICP.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fetch_url` | provider-specific | vendor | maybe |
| `linkedin_api` | provider-specific | vendor | maybe |
| `x_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: ICP + platform tokens.
- **Writes**: Signal events into the trigger stream..

## Side effects

- Emits enriched_record to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
