---
id: tranche_1_budgeter
name: tranche_1_budgeter
artifact_type: agent
lifecycle: project
category: validation
phase: 3
step: 20
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: integrator
mode: pipeline-stage
depends_on: [validation_experiment_designer, channel_economics_modeler]
produces: markdown_report
tools: [read_prior_step]
tags: [budget, tramo-1, capital, calendar, phase-3]
gate: false
optional: false
---

# tranche_1_budgeter

## Identity

```yaml
- name:  tranche_1_budgeter
  queue: hermes-agents
  role:  integrator
  note:  Aggregates experiment budgets and channel benchmarks into a single Capital Tramo 1 figure with go/no-go decision framework.
```

## Purpose

Step 20. Aggregates step 19 experiment budgets and step 17 channel
benchmarks into a single Capital Tramo 1 figure — the total capital
required to find or definitively rule out `CAC < LTV` across the
target segments and channels. Produces low/mid/high, a spend
calendar aligned to experiment batches, and a go/no-go funding
framework.

## Inspiration

`tranche-1-budget` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 17, 19
- **Writes:** `20_tranche_1_budget.md`
- **Upstream:** `validation_experiment_designer`
- **Downstream:** `scaling_gate_definer`

## Structured output

```python
class Tranche1Budget(BaseModel):
    experiment_lines: list[dict[str, float]]
    subtotal_low_eur: float
    subtotal_mid_eur: float
    subtotal_high_eur: float
    safety_buffer_pct: float
    total_low_eur: float
    total_mid_eur: float
    total_high_eur: float
    calendar: str
    funding_decision_framework: str
```

## Prompt shape

- **System:** "Every budget line is anchored to a step-19
  experiment. No experiment, no line."
- **User:** experiment plan + channel benchmarks.

## Extension notes

- Tramo 1 pays for learning, not for scale. Do not include scaling
  ad spend, hiring or product build — those belong to
  `financial_business_planner` (Tramo 2).
