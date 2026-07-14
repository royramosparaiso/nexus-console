---
id: listing_generator
name: listing_generator
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_property, portal_apis]
tags: [listing, portals, real-estate]
gate: false
optional: false
---

# listing_generator

## Identity

```yaml
agents:
  - name: listing_generator
    role: writer
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Writes listing copy + selects hero images + generates floor-plan captions across portals (Idealista, Fotocasa, Zillow).

## Inspiration

Derived from the Business Operations rollout planner — Listing Generator cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_property` | provider-specific | vendor | maybe |
| `portal_apis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Property record + photos.
- **Writes**: Portal-ready listings..
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

- **System**: "You run the Listing Generator job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
