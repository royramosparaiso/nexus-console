---
id: status_updates
name: status_updates
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_pm_board, read_workspace]
tags: [status, weekly-update]
gate: false
optional: false
---

# status_updates

## Identity

```yaml
agents:
  - name: status_updates
    role: writer
    mode: scheduled
    produces: markdown_report
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Weekly rollup for each active project: what shipped, what's next, what's blocked. Auto-sent unless flagged.

## Inspiration

Derived from the Business Operations rollout planner — Status Updates cell in the operations × 4-orchestrate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_pm_board` | provider-specific | vendor | maybe |
| `read_workspace` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Project workspace + PM board.
- **Writes**: Weekly status..
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

- **System**: "You run the Status Updates job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
