---
id: re_comparables_valuation
name: re_comparables_valuation
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [comparables_source, read_analytics]
tags: [comparables, valuation, range, skill, real-estate]
gate: false
optional: false
---

# re_comparables_valuation

## Identity

```yaml
skills:
  - name: re_comparables_valuation
    kind: skill
    produces: structured_json
    domain: intelligence
    verticals: [real-estate]
```

## Purpose

Retrieve comparables for a subject property and derive an explained valuation range (low/mid/high) with the comps and assumptions used. Informational, not a certified appraisal.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `comparables_source` | provider-specific | vendor | maybe |
| `read_analytics` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Subject property facts + comparables source.

## Outputs

Valuation range + comps table + assumptions + caveats.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
