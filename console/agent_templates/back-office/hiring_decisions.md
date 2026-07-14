---
id: hiring_decisions
name: hiring_decisions
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_notes]
tags: [hiring, founder-led]
gate: false
optional: false
---

# hiring_decisions

## Identity

```yaml
agents:
  - name: hiring_decisions
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led. Structures hiring debriefs and drafts offer packages with rationale.

## Inspiration

Derived from the Business Operations rollout planner — Hiring Decisions cell in the back-office × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Interview scorecards.
- **Writes**: Hiring memo..
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

- **System**: "You run the Hiring Decisions job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
