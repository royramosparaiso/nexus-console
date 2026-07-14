---
id: re_portal_field_normalization
name: re_portal_field_normalization
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [read_crm]
tags: [portal, normalization, mapping, skill, real-estate]
gate: false
optional: false
---

# re_portal_field_normalization

## Identity

```yaml
skills:
  - name: re_portal_field_normalization
    kind: skill
    produces: structured_json
    domain: marketing
    verticals: [real-estate]
```

## Purpose

Map internal listing fields to each portal's required schema, validating enumerations/units and reporting unmappable fields.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Internal listing record + target portal schema.

## Outputs

Portal-ready field set + a list of validation issues.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
