---
id: closing_coordination
name: closing_coordination
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 1
verticals: [real-estate]
role: coordinator
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, email]
tags: [closing, escrow, real-estate]
gate: false
optional: false
---

# closing_coordination

## Identity

```yaml
agents:
  - name: closing_coordination
    role: coordinator
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Coordinates closing checklist across buyer, seller, lender, notary — tracks doc collection and dates.

## Inspiration

Derived from the Business Operations rollout planner — Closing Coordination cell in the sales × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal record.
- **Writes**: Closing plan + status..
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

- **System**: "You run the Closing Coordination job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
