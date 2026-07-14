---
id: re_lead_scoring_explainable
name: re_lead_scoring_explainable
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [read_crm]
tags: [scoring, explainable, lead, skill, real-estate]
gate: false
optional: false
---

# re_lead_scoring_explainable

## Identity

```yaml
skills:
  - name: re_lead_scoring_explainable
    kind: skill
    produces: structured_json
    domain: sales
    verticals: [real-estate]
```

## Purpose

Produce an explainable lead score from stated intent, engagement and fit signals, returning the contributing factors alongside the score. No protected-characteristic inputs.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Qualified lead record + engagement signals.

## Outputs

Score + ranked contributing factors (human-readable explanation).

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
