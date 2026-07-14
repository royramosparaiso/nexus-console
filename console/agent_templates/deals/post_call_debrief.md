---
id: post_call_debrief
name: post_call_debrief
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: markdown_report
tools: [read_calls]
tags: [debrief, call]
gate: false
optional: false
---

# post_call_debrief

## Identity

```yaml
agents:
  - name: post_call_debrief
    role: writer
    mode: event-driven
    produces: markdown_report
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

From a call transcript, drafts a structured debrief: attendees, decision-makers, pains raised, next steps, blockers.

## Inspiration

Derived from the Business Operations rollout planner — Post-Call Debrief cell in the deals × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Call transcript.
- **Writes**: Debrief pushed to deal record..
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

- **System**: "You run the Post-Call Debrief job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
