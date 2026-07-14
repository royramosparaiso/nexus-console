---
id: cash_flow_forecasting
name: cash_flow_forecasting
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_ledger, statistical_analysis]
tags: [cash-flow, forecast]
gate: false
optional: false
---

# cash_flow_forecasting

## Identity

```yaml
agents:
  - name: cash_flow_forecasting
    role: analyst
    mode: scheduled
    produces: markdown_report
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Weekly 13-week cash-flow forecast with scenarios, drivers, alerts on runway shrinkage.

## Inspiration

Derived from the Business Operations rollout planner — Cash-Flow Forecasting cell in the back-office × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_ledger` | provider-specific | vendor | maybe |
| `statistical_analysis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ledger + AR + AP + payroll.
- **Writes**: Forecast + scenarios..
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

- **System**: "You run the Cash-Flow Forecasting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
