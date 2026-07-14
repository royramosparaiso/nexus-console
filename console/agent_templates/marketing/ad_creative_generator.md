---
id: ad_creative_generator
name: ad_creative_generator
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_brand_voice]
tags: [ads, creative, copy]
gate: false
optional: false
---

# ad_creative_generator

## Identity

```yaml
agents:
  - name: ad_creative_generator
    role: writer
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Generates ad-variant sets (headlines, primaries, descriptions) per persona and channel — with A/B split annotations.

## Inspiration

Derived from the Business Operations rollout planner — Ad Creative Generator cell in the marketing × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Persona + product + brand voice.
- **Writes**: Ad copy variants..
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

- **System**: "You run the Ad Creative Generator job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
