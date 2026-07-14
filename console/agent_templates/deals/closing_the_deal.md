---
id: closing_the_deal
name: closing_the_deal
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_calls]
tags: [closing, ae-led]
gate: false
optional: false
---

# closing_the_deal

## Identity

```yaml
agents:
  - name: closing_the_deal
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

AE-led card. Drafts closing-call briefs, next-steps emails and mutual action plans for the AE to finalise.

## Inspiration

Derived from the Business Operations rollout planner — Closing the Deal cell in the deals × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_calls` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal record + last touches.
- **Writes**: Closing brief..
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

- **System**: "You run the Closing the Deal job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
