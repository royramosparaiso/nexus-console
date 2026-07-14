---
id: handoff_docs
name: handoff_docs
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_workspace]
tags: [handoff, documentation]
gate: false
optional: false
---

# handoff_docs

## Identity

```yaml
agents:
  - name: handoff_docs
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

From project artefacts, drafts client-facing handoff docs: overview, decisions, ops runbook, contact list, next steps.

## Inspiration

Derived from the Business Operations rollout planner — Handoff Docs cell in the operations × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_workspace` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Project workspace.
- **Writes**: Handoff doc..
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

- **System**: "You run the Handoff Docs job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
