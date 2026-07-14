---
id: scope_change_control
name: scope_change_control
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [marketing-agency]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_email, read_sow]
tags: [scope, change-order, agency]
gate: false
optional: false
---

# scope_change_control

## Identity

```yaml
agents:
  - name: scope_change_control
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Detects scope changes from client messages and drafts change orders with impact analysis.

## Inspiration

Derived from the Business Operations rollout planner — Scope Change Control cell in the marketing × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_email` | provider-specific | vendor | maybe |
| `read_sow` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Client threads + SOW.
- **Writes**: Change order draft..
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

- **System**: "You run the Scope Change Control job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
