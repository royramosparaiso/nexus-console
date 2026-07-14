---
id: contact_enrichment
name: contact_enrichment
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
tools: [clearbit, apollo, hunter]
tags: [enrichment, contact, skill]
gate: false
optional: false
---

# contact_enrichment

## Identity

```yaml
skills:
  - name: contact_enrichment
    kind: skill
    produces: enriched_record
    domain: sales
```

## Purpose

Reusable capability: given a name+company, resolve email, phone, LinkedIn, role, tenure, seniority.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `clearbit` | provider-specific | vendor | maybe |
| `apollo` | provider-specific | vendor | maybe |
| `hunter` | provider-specific | vendor | maybe |

## Inputs

Contact record with partial fields.

## Outputs

Contact record with enriched fields + provenance..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
