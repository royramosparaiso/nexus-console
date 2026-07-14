---
id: re_office_routing
name: re_office_routing
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: connector
mode: event-driven
depends_on: [re_territory_routing]
produces: side_effect
tools: [read_crm, assignment_api]
tags: [routing, territory, assignment, real-estate]
gate: false
optional: false
---

# re_office_routing

## Identity

```yaml
sidecars:
  - name: re_office_routing
    role: connector
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
    verticals: [real-estate]
```

## Purpose

Territory/office routing, workload-aware across the 5 agents in each office. Assigns leads to Madrid or Marbella and to an available agent based on territory + current load.

## Trigger

Reacts to qualified-lead events.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `assignment_api` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Qualified lead (territory, language) + per-agent workload.
- **Writes**: An office+agent assignment; overflow signal when a branch is saturated.
- **Depends on**: `re_territory_routing`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
