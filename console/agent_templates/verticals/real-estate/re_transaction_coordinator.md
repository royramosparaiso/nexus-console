---
id: re_transaction_coordinator
name: re_transaction_coordinator
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: coordinator
mode: single-shot
depends_on: [re_transaction_doc_checklist, re_kyc_aml_triage]
produces: markdown_report
tools: [read_crm, document_store, calendar_api]
tags: [transaction, closing, coordination, real-estate]
gate: false
optional: false
---

# re_transaction_coordinator

## Identity

```yaml
agents:
  - name: re_transaction_coordinator
    role: coordinator
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Transaction/closing coordinator. Tracks an accepted offer through to completion: document checklist, KYC/AML checklist status, deadlines (deposit, notary, completion) and stakeholder updates.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `document_store` | provider-specific | vendor | maybe |
| `calendar_api` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Accepted-offer record, document/KYC checklist status, key dates.
- **Writes**: A transaction status report with outstanding items and next deadlines.
- **Upstream**: Offer/negotiation coordinator and KYC/AML triage.
- **Downstream**: After-sales/referral agent on completion.
- **Depends on**: `re_transaction_doc_checklist`, `re_kyc_aml_triage`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_transaction_coordinator role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Surfaces KYC/AML and document status as checklist flags for human/legal review. Never marks a compliance item as cleared on its own.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
