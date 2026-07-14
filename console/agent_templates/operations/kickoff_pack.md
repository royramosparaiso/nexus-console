---
id: kickoff_pack
name: kickoff_pack
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: pdf
tools: [proposal_templates, write_pdf]
tags: [kickoff, onboarding]
gate: false
optional: false
---

# kickoff_pack

## Identity

```yaml
agents:
  - name: kickoff_pack
    role: writer
    mode: single-shot
    produces: pdf
    domain: operations
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Assembles the client kickoff pack: goals, roles, timeline, comms cadence, escalation path, artefacts.

## Inspiration

Derived from the Business Operations rollout planner — Kickoff Pack cell in the operations × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `proposal_templates` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Project brief.
- **Writes**: Kickoff pack PDF..
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

- **System**: "You run the Kickoff Pack job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
