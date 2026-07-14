---
id: event_planning
name: event_planning
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 1
verticals: [any]
role: coordinator
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_brand_voice]
tags: [events, planning]
gate: false
optional: false
---

# event_planning

## Identity

```yaml
agents:
  - name: event_planning
    role: coordinator
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Plans an event end-to-end: goals, format, target audience, run of show, promo plan, follow-up plan.

## Inspiration

Derived from the Business Operations rollout planner — Event Planning cell in the marketing × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Event brief.
- **Writes**: Event plan..
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

- **System**: "You run the Event Planning job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
