---
id: creative_pipeline
name: creative_pipeline
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [marketing-agency]
role: coordinator
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_pm_board, timesheet_api]
tags: [pipeline, capacity, agency]
gate: false
optional: false
---

# creative_pipeline

## Identity

```yaml
agents:
  - name: creative_pipeline
    role: coordinator
    mode: scheduled
    produces: markdown_report
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Balances creative team capacity vs demand across clients; proposes rebalance and hiring signals.

## Inspiration

Derived from the Business Operations rollout planner — Creative Pipeline cell in the marketing × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_pm_board` | provider-specific | vendor | maybe |
| `timesheet_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: PM board + timesheets.
- **Writes**: Pipeline plan..
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

- **System**: "You run the Creative Pipeline job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
