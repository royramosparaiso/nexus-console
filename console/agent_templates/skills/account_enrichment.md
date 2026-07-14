---
id: account_enrichment
name: account_enrichment
artifact_type: skill
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: null
mode: null
depends_on: []
produces: enriched_record
tools: [clearbit, builtwith, crunchbase]
tags: [enrichment, account, skill, firmographics]
gate: false
optional: false
---

# account_enrichment

## Identity

```yaml
skills:
  - name: account_enrichment
    kind: skill
    produces: enriched_record
    domain: sales
```

## Purpose

Reusable capability: given a domain, resolve firmographics, tech stack, funding, headcount, geo.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `clearbit` | provider-specific | vendor | maybe |
| `builtwith` | provider-specific | vendor | maybe |
| `crunchbase` | provider-specific | vendor | maybe |

## Inputs

Domain.

## Outputs

Firmographic bundle..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
