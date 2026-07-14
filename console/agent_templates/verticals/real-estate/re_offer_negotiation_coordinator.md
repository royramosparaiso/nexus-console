---
id: re_offer_negotiation_coordinator
name: re_offer_negotiation_coordinator
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 2
verticals: [real-estate]
role: coordinator
mode: single-shot
depends_on: [re_offer_comparison_brief]
produces: decision
tools: [read_crm, document_store]
tags: [offer, negotiation, approval, real-estate]
gate: false
optional: false
---

# re_offer_negotiation_coordinator

## Identity

```yaml
agents:
  - name: re_offer_negotiation_coordinator
    role: coordinator
    mode: single-shot
    produces: decision
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
    verticals: [real-estate]
```

## Purpose

Offer & negotiation coordinator. Structures offers, prepares a side-by-side comparison and a negotiation brief, and routes every counter/acceptance through an explicit human approval gate.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `document_store` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Buyer offers, seller position, comparison brief.
- **Writes**: A recommended next step (decision) that a human agent must approve before it is sent.
- **Upstream**: Offer comparison skill and buyer/seller flows.
- **Downstream**: Transaction coordinator once an offer is accepted (by humans).
- **Depends on**: `re_offer_comparison_brief`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_offer_negotiation_coordinator role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- **No offer, counter-offer or acceptance is ever sent autonomously.** The agent proposes; a named human agent approves. Approval events are audited.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
