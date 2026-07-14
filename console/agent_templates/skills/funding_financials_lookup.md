---
id: funding_financials_lookup
name: funding_financials_lookup
artifact_type: skill
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [crunchbase, sec_edgar, linkedin_api]
tags: [funding, financials, skill]
gate: false
optional: false
---

# funding_financials_lookup

## Identity

```yaml
skills:
  - name: funding_financials_lookup
    kind: skill
    produces: structured_json
    domain: intelligence
```

## Purpose

Reusable capability: resolves funding rounds, investors, filings, headcount ranges from public sources.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `crunchbase` | provider-specific | vendor | maybe |
| `sec_edgar` | provider-specific | vendor | maybe |
| `linkedin_api` | provider-specific | vendor | maybe |

## Inputs

Company name.

## Outputs

Structured funding record..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
