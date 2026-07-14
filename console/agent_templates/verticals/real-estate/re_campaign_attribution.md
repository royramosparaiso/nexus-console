---
id: re_campaign_attribution
name: re_campaign_attribution
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_analytics, read_crm]
tags: [campaign, attribution, performance, real-estate]
gate: false
optional: false
---

# re_campaign_attribution

## Identity

```yaml
sidecars:
  - name: re_campaign_attribution
    role: worker
    mode: scheduled
    produces: side_effect
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
    verticals: [real-estate]
```

## Purpose

Campaign attribution/performance collector. Attributes leads/viewings/offers back to source campaigns and collects performance metrics for the weekly review.

## Trigger

Runs on a schedule (`${ATTRIBUTION_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_analytics` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Campaign touch data + CRM lead lineage.
- **Writes**: Attributed performance rollups per campaign/office.
- **Depends on**: —

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
