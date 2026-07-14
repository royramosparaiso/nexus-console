---
id: re_transaction_doc_checklist
name: re_transaction_doc_checklist
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [document_store]
tags: [documents, checklist, transaction, skill, real-estate]
gate: false
optional: false
---

# re_transaction_doc_checklist

## Identity

```yaml
skills:
  - name: re_transaction_doc_checklist
    kind: skill
    produces: structured_json
    domain: back-office
    verticals: [real-estate]
```

## Purpose

Build and track the document checklist for a listing/transaction (ownership, energy certificate, licences, community/debt certificates) as flags for human/legal review.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `document_store` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Property/transaction type + attached documents.

## Outputs

Document checklist with per-item status flags.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
