---
id: re_buyer_advisor
name: re_buyer_advisor
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
role: analyst
mode: single-shot
depends_on: [re_requirements_normalization, re_property_matching_rank]
produces: structured_json
tools: [read_crm, search_inventory]
tags: [buyer, matching, advisory, real-estate]
gate: false
optional: false
---

# re_buyer_advisor

## Identity

```yaml
agents:
  - name: re_buyer_advisor
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Buyer advisor. Turns a buyer's normalized requirements into a ranked shortlist with a plain-language rationale per property, so the human agent can advise with context.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `search_inventory` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Normalized buyer brief + ranked candidate properties.
- **Writes**: A shortlist with per-match reasoning and open questions for the buyer.
- **Upstream**: Requirements normalization skill and the matching-refresh sidecar.
- **Downstream**: Viewing coordinator and the offer/negotiation flow.
- **Depends on**: `re_requirements_normalization`, `re_property_matching_rank`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_buyer_advisor role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Ranking is decision-support. It never filters on protected characteristics; routing/matching operate on stated property criteria only.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
