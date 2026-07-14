---
id: re_visit_route_sync
name: re_visit_route_sync
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: connector
mode: event-driven
depends_on: [re_viewing_scheduling]
produces: side_effect
tools: [calendar_api, maps_api]
tags: [calendar, route, sync, real-estate]
gate: false
optional: false
---

# re_visit_route_sync

## Identity

```yaml
sidecars:
  - name: re_visit_route_sync
    role: connector
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 3-generate
    autonomy: fully-autonomous
    verticals: [real-estate]
```

## Purpose

Calendar/visit route sync. Syncs confirmed viewings to agent calendars and computes an efficient visit order per agent per day.

## Trigger

Reacts to viewing-confirmed events.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `calendar_api` | provider-specific | vendor | maybe |
| `maps_api` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Confirmed viewings + agent calendars/locations.
- **Writes**: Calendar events + an ordered daily visit route.
- **Depends on**: `re_viewing_scheduling`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
