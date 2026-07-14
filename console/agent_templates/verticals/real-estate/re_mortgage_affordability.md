---
id: re_mortgage_affordability
name: re_mortgage_affordability
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
tags: [mortgage, affordability, scenario, skill, real-estate]
gate: false
optional: false
---

# re_mortgage_affordability

## Identity

```yaml
skills:
  - name: re_mortgage_affordability
    kind: skill
    produces: structured_json
    domain: back-office
    verticals: [real-estate]
```

## Purpose

Compute illustrative mortgage affordability scenarios from user-supplied inputs and configurable rate/term assumptions. Informational only — not financial advice and not a lending decision.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

User-supplied income/deposit + configurable assumptions (`${MORTGAGE_ASSUMPTIONS_REF}`).

## Outputs

Illustrative affordability scenarios with stated assumptions and disclaimer.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
