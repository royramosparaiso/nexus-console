---
id: architecture_decisions
name: architecture_decisions
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
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_notes]
tags: [adr, architecture, operator-led]
gate: false
optional: false
---

# architecture_decisions

## Identity

```yaml
agents:
  - name: architecture_decisions
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Operator-led. Drafts ADRs: context, decision, alternatives, consequences.

## Inspiration

Derived from the Business Operations rollout planner — Architecture Decisions cell in the operations × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Design discussions.
- **Writes**: ADR doc..
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

- **System**: "You run the Architecture Decisions job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
