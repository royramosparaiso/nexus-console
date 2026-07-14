---
id: re_listing_marketing_manager
name: re_listing_marketing_manager
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: writer
mode: single-shot
depends_on: [re_listing_copy_bilingual, re_portal_field_normalization]
produces: structured_json
tools: [document_store, image_pipeline]
tags: [listing, content, marketing, real-estate]
gate: false
optional: false
---

# re_listing_marketing_manager

## Identity

```yaml
agents:
  - name: re_listing_marketing_manager
    role: writer
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Listing marketing/content manager. Assembles the marketing package for an approved listing: bilingual copy, photo/floorplan checklist, portal-ready field set and a channel plan.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `document_store` | provider-specific | vendor | maybe |
| `image_pipeline` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Approved listing facts + media assets.
- **Writes**: A marketing package (copy ES/EN, asset checklist, portal field map).
- **Upstream**: Listing acquisition manager (post human approval).
- **Downstream**: Portal syndication sidecar and campaign attribution.
- **Depends on**: `re_listing_copy_bilingual`, `re_portal_field_normalization`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_listing_marketing_manager role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Copy avoids unverifiable superlatives and legal claims; energy-certificate and licence fields are placeholders the agent flags for the human to fill.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
