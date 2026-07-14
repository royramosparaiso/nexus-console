---
id: content_calendar
name: content_calendar
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 2
verticals: [any]
role: coordinator
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_brand_voice, read_prior_step]
tags: [calendar, planning]
gate: false
optional: false
---

# content_calendar

## Identity

```yaml
agents:
  - name: content_calendar
    role: coordinator
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 1-foundation
    autonomy: human-assisted
```

## Purpose

Builds a quarterly calendar with themes, channels, cadence and owners — human approves before it schedules.

## Inspiration

Derived from the Business Operations rollout planner — Content Calendar cell in the marketing × 1-foundation × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |
| `read_prior_step` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Marketing goals + brand voice.
- **Writes**: Calendar tables per channel..
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

- **System**: "You run the Content Calendar job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
