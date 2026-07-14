---
id: brief_generation
name: brief_generation
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
produces: markdown_report
tools: [read_brand_voice]
tags: [brief, creative, agency]
gate: false
optional: false
---

# brief_generation

## Identity

```yaml
agents:
  - name: brief_generation
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Turns a request into a full creative brief — objective, audience, insight, tone, mandatories, deliverables, deadlines.

## Inspiration

Derived from the Business Operations rollout planner — Brief Generation cell in the marketing × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Request thread + brand voice.
- **Writes**: Creative brief..
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

- **System**: "You run the Brief Generation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
