---
id: re_listing_acquisition_manager
name: re_listing_acquisition_manager
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: writer
mode: single-shot
depends_on: [re_transaction_doc_checklist, re_comparables_valuation]
produces: markdown_report
tools: [read_crm, document_store]
tags: [seller, listing, acquisition, real-estate]
gate: false
optional: false
---

# re_listing_acquisition_manager

## Identity

```yaml
agents:
  - name: re_listing_acquisition_manager
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 3-generate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Seller/listing acquisition manager. Prepares the listing-mandate case for a prospective seller: ownership/document checklist status, valuation-support summary and a proposed acquisition plan for the human agent to present.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `document_store` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Seller lead, property facts, document-checklist status, comparables range.
- **Writes**: An acquisition brief + mandate readiness checklist (draft, for human sign-off).
- **Upstream**: Lead concierge (seller-intent) and the document-completeness monitor.
- **Downstream**: Human agent approval, then listing marketing + valuation support.
- **Depends on**: `re_transaction_doc_checklist`, `re_comparables_valuation`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_listing_acquisition_manager role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Property-document and ownership checks are **flags only**; legal validity of title/mandate is confirmed by the agency's lawyer, never asserted here.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
