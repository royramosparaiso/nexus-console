---
id: analytics_rollup
name: analytics_rollup
artifact_type: sidecar
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [ga4_api, meta_ads_api, google_ads_api]
tags: [analytics, rollup, digest]
gate: false
optional: false
---

# analytics_rollup

## Identity

```yaml
sidecars:
  - name: analytics_rollup
    role: worker
    mode: scheduled
    produces: side_effect
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Nightly pull from GA4, ad platforms and CRM into a unified table — sends weekly digest with anomalies flagged.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `ga4_api` | provider-specific | vendor | maybe |
| `meta_ads_api` | provider-specific | vendor | maybe |
| `google_ads_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: GA4 + ad platforms + CRM.
- **Writes**: Unified table + weekly digest..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
