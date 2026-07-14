---
id: re_offer_comparison_brief
name: re_offer_comparison_brief
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm, read_crm]
tags: [offer, comparison, negotiation, skill, real-estate]
gate: false
optional: false
---

# re_offer_comparison_brief

## Identity

```yaml
skills:
  - name: re_offer_comparison_brief
    kind: skill
    produces: structured_json
    domain: deals
    verticals: [real-estate]
```

## Purpose

Compare competing offers on price, conditions, financing and timeline, and produce a concise negotiation brief. Decision-support for the human agent.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Set of offers + seller priorities.

## Outputs

Comparison table + negotiation brief (no autonomous action).

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
