---
id: web_maps_scraping
name: web_maps_scraping
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
tools: [fetch_url, wide_browse, geocode]
tags: [scraping, maps, local, geo]
gate: false
optional: false
---

# web_maps_scraping

## Identity

```yaml
sidecars:
  - name: web_maps_scraping
    role: worker
    mode: scheduled
    produces: enriched_record
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Pulls prospect signals from public web and geographic sources — Google Maps listings, review sites, industry directories.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fetch_url` | provider-specific | vendor | maybe |
| `wide_browse` | provider-specific | vendor | maybe |
| `geocode` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Vertical + geo scope.
- **Writes**: Enriched prospect records with geo + business metadata..

## Side effects

- Emits enriched_record to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
