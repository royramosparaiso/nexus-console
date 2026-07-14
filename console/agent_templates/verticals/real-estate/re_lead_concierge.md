---
id: re_lead_concierge
name: re_lead_concierge
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 3
verticals: [real-estate]
role: classifier
mode: event-driven
depends_on: [re_lead_qualification_bilingual, re_consent_gdpr_handling, re_lead_scoring_explainable]
produces: structured_json
tools: [read_crm, email, whatsapp_api]
tags: [lead, qualification, concierge, real-estate]
gate: false
optional: false
---

# re_lead_concierge

## Identity

```yaml
agents:
  - name: re_lead_concierge
    role: classifier
    mode: event-driven
    produces: structured_json
    domain: sales
    rollout_stage: 2-capture
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Inbound lead concierge. First touch for every buyer/seller enquiry across web forms, portals, phone and messaging. Qualifies intent (buy/sell/rent), captures consent state, detects language (ES/EN) and hands a scored, deduplicated lead to office routing.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |
| `whatsapp_api` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Raw inbound enquiries + existing CRM contacts.
- **Writes**: A qualified, consent-tagged lead record with an explainable score.
- **Upstream**: Portal/webhook capture and the CRM dedupe sidecar.
- **Downstream**: Office/territory routing and the buyer or seller flow.
- **Depends on**: `re_lead_qualification_bilingual`, `re_consent_gdpr_handling`, `re_lead_scoring_explainable`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_lead_concierge role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Never auto-replies with commitments (price, availability, legal terms) — drafts only; a human agent confirms. Response timing is governed by `${LEAD_RESPONSE_SLA_MINUTES}`.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
