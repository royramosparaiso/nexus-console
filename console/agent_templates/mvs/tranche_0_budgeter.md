---
id: tranche_0_budgeter
name: tranche_0_budgeter
artifact_type: agent
lifecycle: project
category: mvs
phase: 2
step: 15
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: integrator
mode: pipeline-stage
depends_on: [resource_inventory_analyst, legal_setup_cost_estimator, mvp_scoper, minimal_tech_stack_cost_estimator]
produces: markdown_report
tools: [read_prior_step]
tags: [budget, tramo-0, capital, cash-flow, phase-2, phase-boundary]
gate: false
optional: false
---

# tranche_0_budgeter

## Identity

```yaml
- name:  tranche_0_budgeter
  queue: hermes-agents
  role:  integrator
  note:  Consolidates steps 11-14 into a single Capital Tramo 0 figure with low/mid/high range and monthly cash flow.
```

## Purpose

Step 15, final consolidation of Phase 2. Aggregates the outputs of
steps 11-14 into a single Capital Tramo 0 figure — the total
minimum capital required for the project to legally exist, run an
MVP and enter validation. Produces a low/mid/high range, a monthly
cash-flow projection, a deployment calendar and a 15-25% safety
buffer.

## Inspiration

`tranche-0-budget` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 11-14 outputs
- **Writes:** `15_tranche_0_budget.md`
- **Upstream:** `resource_inventory_analyst`, `legal_setup_cost_estimator`, `mvp_scoper`, `minimal_tech_stack_cost_estimator`
- **Downstream:** Phase-3 templates

## Structured output

```python
class BudgetLine(BaseModel):
    source_step: int
    item: str
    cost_low_eur: float
    cost_mid_eur: float
    cost_high_eur: float

class Tranche0Budget(BaseModel):
    lines: list[BudgetLine]
    subtotal_low_eur: float
    subtotal_mid_eur: float
    subtotal_high_eur: float
    safety_buffer_pct: float
    total_low_eur: float
    total_mid_eur: float
    total_high_eur: float
    monthly_cash_flow: dict[str, float]   # "2026-08" -> EUR
    deployment_calendar: str              # markdown
```

## Prompt shape

- **System:** "You are an integrator, not a researcher. Every euro
  traces to a step 11-14 line. If a category is missing (e.g. legal
  step never ran), abort — do not extrapolate."
- **User:** paths to steps 11-14.

## Extension notes

- Safety buffer defaults to 20%. Below 15% is optimistic; above 25%
  hides that the founder is padding an unrealistic scope.
