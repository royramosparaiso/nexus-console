---
id: scope_calls
name: scope_calls
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 1-foundation
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_calls]
tags: [scope, sow, operator-led]
gate: false
optional: false
---

# scope_calls

## Identity

```yaml
agents:
  - name: scope_calls
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Operator-led. Turns discovery-call transcripts into scoped statements of work.

## Inspiration

Derived from the Business Operations rollout planner — Scope Calls cell in the operations × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Discovery call transcript.
- **Writes**: Scope doc..
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

- **System**: "You run the Scope Calls job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
