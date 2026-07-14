---
id: client_trust
name: client_trust
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_notes]
tags: [client-comms, trust, operator-led]
gate: false
optional: false
---

# client_trust

## Identity

```yaml
agents:
  - name: client_trust
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Operator-led. Drafts trust-building comms: honest updates, escalation letters, apology + remediation letters.

## Inspiration

Derived from the Business Operations rollout planner — Client Trust cell in the operations × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Situation notes.
- **Writes**: Comms drafts..
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

- **System**: "You run the Client Trust job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
