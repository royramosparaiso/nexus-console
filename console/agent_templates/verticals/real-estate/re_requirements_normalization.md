---
id: re_requirements_normalization
name: re_requirements_normalization
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
tools: [llm]
tags: [requirements, normalization, buyer, skill, real-estate]
gate: false
optional: false
---

# re_requirements_normalization

## Identity

```yaml
skills:
  - name: re_requirements_normalization
    kind: skill
    produces: structured_json
    domain: sales
    verticals: [real-estate]
```

## Purpose

Normalize a buyer's free-text requirements into a structured brief (type, beds, budget band, zones, must-haves/nice-to-haves) for matching.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Free-text buyer requirements (ES/EN).

## Outputs

Structured, normalized buyer brief.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
