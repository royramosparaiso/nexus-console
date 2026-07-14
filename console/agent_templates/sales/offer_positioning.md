---
id: offer_positioning
name: offer_positioning
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_product_docs, read_prior_step]
tags: [positioning, offer, founder-led]
gate: false
optional: false
---

# offer_positioning

## Identity

```yaml
agents:
  - name: offer_positioning
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led card. Drafts positioning statements, offer packages and pricing tiers for the founder to iterate on.

## Inspiration

Derived from the Business Operations rollout planner — Offer & Positioning cell in the sales × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_product_docs` | provider-specific | vendor | maybe |
| `read_prior_step` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Product docs + market research.
- **Writes**: Positioning + offers doc..
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

- **System**: "You run the Offer & Positioning job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
