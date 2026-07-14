---
id: re_consent_gdpr_handling
name: re_consent_gdpr_handling
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [read_crm]
tags: [consent, gdpr, compliance, skill, real-estate]
gate: false
optional: false
---

# re_consent_gdpr_handling

## Identity

```yaml
skills:
  - name: re_consent_gdpr_handling
    kind: skill
    produces: structured_json
    domain: back-office
    verticals: [real-estate]
```

## Purpose

Normalize and evaluate consent/GDPR status per contact and channel (basis, source, timestamp, withdrawal). Produces a checklist and a contactability flag — it does not grant legal compliance.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Contact record + consent events.

## Outputs

Per-channel consent state + contactability flag + review notes.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
