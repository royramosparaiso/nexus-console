---
id: re_viewing_scheduling
name: re_viewing_scheduling
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [calendar_api, maps_api]
tags: [scheduling, route, viewing, skill, real-estate]
gate: false
optional: false
---

# re_viewing_scheduling

## Identity

```yaml
skills:
  - name: re_viewing_scheduling
    kind: skill
    produces: structured_json
    domain: operations
    verticals: [real-estate]
```

## Purpose

Propose viewing slots against agent availability and optimize the daily visit route across a set of confirmed viewings.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `calendar_api` | provider-specific | vendor | maybe |
| `maps_api` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Requested viewings + agent availability + property locations.

## Outputs

Proposed slots + an optimized route order.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
