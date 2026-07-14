---
id: re_market_listing_watcher
name: re_market_listing_watcher
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: intelligence
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [portal_api, read_analytics]
tags: [market, price-change, watcher, real-estate]
gate: false
optional: false
---

# re_market_listing_watcher

## Identity

```yaml
sidecars:
  - name: re_market_listing_watcher
    role: worker
    mode: scheduled
    produces: side_effect
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Price-change/market-listing watcher. Tracks comparable public listings for price changes and new/removed inventory in each territory and emits change signals.

## Trigger

Runs on a schedule (`${MARKET_WATCH_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `portal_api` | provider-specific | vendor | maybe |
| `read_analytics` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Watched comparable listings per territory.
- **Writes**: Change signals (price/status/new/removed) for downstream rematch.
- **Depends on**: —

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
