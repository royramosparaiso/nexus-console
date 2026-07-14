---
id: landing_page_writer
name: landing_page_writer
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_brand_voice, proof_matching]
tags: [landing-page, copy]
gate: false
optional: false
---

# landing_page_writer

## Identity

```yaml
agents:
  - name: landing_page_writer
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts full landing-page copy: hero, sub-hero, sections, social proof placement, CTAs — matched to campaign source.

## Inspiration

Derived from the Business Operations rollout planner — Landing Page Writer cell in the marketing × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |
| `proof_matching` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Campaign spec + brand voice + proof library.
- **Writes**: Landing copy markdown..
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

- **System**: "You run the Landing Page Writer job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
