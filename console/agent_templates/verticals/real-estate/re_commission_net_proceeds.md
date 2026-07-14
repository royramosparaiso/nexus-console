---
id: re_commission_net_proceeds
name: re_commission_net_proceeds
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm]
tags: [commission, net-proceeds, scenario, skill, real-estate]
gate: false
optional: false
---

# re_commission_net_proceeds

## Identity

```yaml
skills:
  - name: re_commission_net_proceeds
    kind: skill
    produces: structured_json
    domain: back-office
    verticals: [real-estate]
```

## Purpose

Calculate commission and estimated seller net-proceeds scenarios from configurable fee/tax assumptions. Illustrative; taxes/fees confirmed by the relevant professional.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Sale price scenario + configurable fee/tax assumptions.

## Outputs

Commission + net-proceeds scenarios with assumptions and caveats.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
