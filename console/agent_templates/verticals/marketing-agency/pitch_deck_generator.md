---
id: pitch_deck_generator
name: pitch_deck_generator
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [marketing-agency]
role: writer
mode: single-shot
depends_on: []
produces: pptx
tools: [case_studies, write_pptx]
tags: [pitch, new-business, agency]
gate: false
optional: false
---

# pitch_deck_generator

## Identity

```yaml
agents:
  - name: pitch_deck_generator
    role: writer
    mode: single-shot
    produces: pptx
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Generates a bespoke pitch deck per new-business opportunity from the case-study library.

## Inspiration

Derived from the Business Operations rollout planner — Pitch Deck Generator cell in the marketing × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `case_studies` | provider-specific | vendor | maybe |
| `write_pptx` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Opportunity brief + case studies.
- **Writes**: Pitch deck..
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

- **System**: "You run the Pitch Deck Generator job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
