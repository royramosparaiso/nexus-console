---
id: sop_generation
name: sop_generation
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 1-foundation
autonomy: human-led
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_calls, read_notes]
tags: [sop, process, operator-led]
gate: false
optional: false
---

# sop_generation

## Identity

```yaml
agents:
  - name: sop_generation
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Operator-led. Turns process descriptions and call transcripts into codified SOPs with steps, roles and checklists.

## Inspiration

Derived from the Business Operations rollout planner — SOP Generation cell in the operations × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Process description + transcripts.
- **Writes**: SOP doc..
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

- **System**: "You run the SOP Generation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
