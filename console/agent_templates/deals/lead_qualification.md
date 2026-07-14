---
id: lead_qualification
name: lead_qualification
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: structured_json
tools: [fit_scoring, read_crm]
tags: [qualification, meddpicc, bant]
gate: false
optional: false
---

# lead_qualification

## Identity

```yaml
agents:
  - name: lead_qualification
    role: classifier
    mode: event-driven
    produces: structured_json
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Qualifies inbound leads against MEDDPICC/BANT + ICP fit and either books a meeting, nurtures, or disqualifies with reason.

## Inspiration

Derived from the Business Operations rollout planner — Lead Qualification cell in the deals × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fit_scoring` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Lead record + fit score.
- **Writes**: Qualification decision..
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

- **System**: "You run the Lead Qualification job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
