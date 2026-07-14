---
id: re_kyc_aml_triage
name: re_kyc_aml_triage
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-led
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [document_store]
tags: [kyc, aml, triage, skill, real-estate]
gate: false
optional: false
---

# re_kyc_aml_triage

## Identity

```yaml
skills:
  - name: re_kyc_aml_triage
    kind: skill
    produces: structured_json
    domain: back-office
    verticals: [real-estate]
```

## Purpose

Triage KYC/AML checklist items (identity, source-of-funds evidence, PEP/sanctions screening references) into a status list for the compliance officer. **Never** decides or approves; flags only.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `document_store` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Client/transaction record + submitted evidence references.

## Outputs

KYC/AML checklist status + items requiring human decision.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
