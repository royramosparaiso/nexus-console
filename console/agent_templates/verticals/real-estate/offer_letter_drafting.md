---
id: offer_letter_drafting
name: offer_letter_drafting
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
depends_on: []
produces: pdf
tools: [contract_templates, write_pdf]
tags: [offer, contract, real-estate]
gate: false
optional: false
---

# offer_letter_drafting

## Identity

```yaml
agents:
  - name: offer_letter_drafting
    role: writer
    mode: single-shot
    produces: pdf
    domain: sales
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts offer letters and counter-offers with contingencies pre-populated from state templates.

## Inspiration

Derived from the Business Operations rollout planner — Offer Letter Drafting cell in the sales × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `contract_templates` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Offer terms + property.
- **Writes**: Offer letter PDF..
- **Upstream**: signals or artefacts from foundation-stage cards in the same domain.
- **Downstream**: consumed by orchestration-stage cards or the human operator.

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the Offer Letter Drafting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
