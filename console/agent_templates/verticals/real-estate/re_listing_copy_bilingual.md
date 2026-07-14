---
id: re_listing_copy_bilingual
name: re_listing_copy_bilingual
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm]
tags: [copy, bilingual, listing, skill, real-estate]
gate: false
optional: false
---

# re_listing_copy_bilingual

## Identity

```yaml
skills:
  - name: re_listing_copy_bilingual
    kind: skill
    produces: structured_json
    domain: marketing
    verticals: [real-estate]
```

## Purpose

Draft listing copy in Spanish and English from structured facts, avoiding unverifiable claims and leaving regulated fields (energy rating, licences) as flagged placeholders.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Structured listing facts.

## Outputs

ES + EN listing copy with flagged placeholders for regulated fields.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
