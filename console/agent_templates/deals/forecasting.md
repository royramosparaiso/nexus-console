---
id: forecasting
name: forecasting
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 3
verticals: [any]
role: analyst
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_crm, read_activity]
tags: [forecast, pipeline]
gate: false
optional: false
---

# forecasting

## Identity

```yaml
agents:
  - name: forecasting
    role: analyst
    mode: scheduled
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Weekly forecast rollup — commit/best-case/pipeline, deal-level probability recalibrated from stage + last-touch signals.

## Inspiration

Derived from the Business Operations rollout planner — Forecasting cell in the deals × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_activity` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal + activity data.
- **Writes**: Forecast with confidence..
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

- **System**: "You run the Forecasting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
