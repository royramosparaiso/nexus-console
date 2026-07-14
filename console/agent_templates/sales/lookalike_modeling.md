---
id: lookalike_modeling
name: lookalike_modeling
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, statistical_analysis]
tags: [lookalike, segmentation, modeling]
gate: false
optional: false
---

# lookalike_modeling

## Identity

```yaml
agents:
  - name: lookalike_modeling
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 1-foundation
    autonomy: human-assisted
```

## Purpose

Given closed-won accounts, derives statistical lookalike criteria and proposes new target segments for human approval.

## Inspiration

Derived from the Business Operations rollout planner — Lookalike Modeling cell in the sales × 1-foundation × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `statistical_analysis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Closed-won CRM data.
- **Writes**: Segment proposals with match rationale..
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

- **System**: "You run the Lookalike Modeling job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
