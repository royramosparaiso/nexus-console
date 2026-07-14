---
id: ltv_cac_targeter
name: ltv_cac_targeter
category: validation
phase: 3
step: 18
role: analyst
mode: pipeline-stage
depends_on: [pricing_strategist, channel_economics_modeler]
produces: markdown_report
tools: [read_prior_step]
tags: [ltv, cac, unit-economics, threshold, phase-3]
gate: false
optional: false
---

# ltv_cac_targeter

## Identity

```yaml
- name:  ltv_cac_targeter
  queue: hermes-agents
  role:  analyst
  note:  Minimum defensible LTV per segment and target CAC ceiling (LTV/3), giving experiments their numerical success threshold.
```

## Purpose

Step 18. Uses pricing (step 8) to compute the minimum defensible LTV
per validated segment. Derives target CAC = LTV / 3 (adjustable per
segment). Defines precisely what "validated" means numerically for
each hypothesis — gives steps 19 and 20 the thresholds they need.
Cross-checks against channel benchmarks (step 17).

## Inspiration

`ltv-cac-targets` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 8, 17
- **Writes:** `18_ltv_cac_targets.md`
- **Upstream:** `pricing_strategist`, `channel_economics_modeler`
- **Downstream:** `validation_experiment_designer`, `tranche_1_budgeter`, `scaling_gate_definer`

## Structured output

```python
class LtvCacTarget(BaseModel):
    segment: str
    arpu_monthly_eur: float
    churn_monthly_pct: float
    gross_margin_pct: float
    ltv_eur: float
    target_cac_multiplier: float           # default 3
    target_cac_eur: float
    benchmark_cac_eur: float                # from step 17
    feasibility: Literal["comfortable", "tight", "at_edge", "infeasible"]

class LtvCacReport(BaseModel):
    targets: list[LtvCacTarget]
    infeasible_segments: list[str]
```

## Prompt shape

- **System:** "LTV = ARPU × gross_margin / monthly_churn. If churn
  is unknown, use a conservative 5%/month and flag it. Do not use an
  optimistic churn to make an infeasible segment look feasible."
- **User:** pricing + channel benchmarks.

## Extension notes

- Segments in `infeasible_segments` should be dropped from step 19
  experiments — spending Tramo 1 on infeasible unit economics is
  waste.
