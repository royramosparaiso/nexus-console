---
id: re_territory_routing
name: re_territory_routing
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [geo_lookup]
tags: [routing, territory, capacity, skill, real-estate]
gate: false
optional: false
---

# re_territory_routing

## Identity

```yaml
skills:
  - name: re_territory_routing
    kind: skill
    produces: structured_json
    domain: sales
    verticals: [real-estate]
```

## Purpose

Decide the owning office (Madrid/Marbella) and balance load across the 5 agents per office using territory rules + current workload. Operates on property/location and capacity only.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `geo_lookup` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Lead location/territory + per-agent capacity snapshot.

## Outputs

Recommended office + agent, with an overflow flag and rationale.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
