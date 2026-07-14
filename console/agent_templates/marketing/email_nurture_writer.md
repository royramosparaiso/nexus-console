---
id: email_nurture_writer
name: email_nurture_writer
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_brand_voice]
tags: [nurture, email, lifecycle]
gate: false
optional: false
---

# email_nurture_writer

## Identity

```yaml
agents:
  - name: email_nurture_writer
    role: writer
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Drafts nurture sequences for each persona / lifecycle stage — welcome, activation, re-engagement.

## Inspiration

Derived from the Business Operations rollout planner — Email Nurture Writer cell in the marketing × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Persona + product + brand voice.
- **Writes**: Sequence draft..
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

- **System**: "You run the Email Nurture Writer job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
