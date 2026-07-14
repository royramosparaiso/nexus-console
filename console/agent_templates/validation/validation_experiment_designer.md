---
id: validation_experiment_designer
name: validation_experiment_designer
artifact_type: agent
lifecycle: project
category: validation
phase: 3
step: 19
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [validation_hypotheses_analyst, channel_economics_modeler, ltv_cac_targeter]
produces: markdown_report
tools: [read_prior_step]
tags: [experiments, landing, outbound, content, seo, phase-3]
gate: false
optional: false
---

# validation_experiment_designer

## Identity

```yaml
- name:  validation_experiment_designer
  queue: hermes-agents
  role:  analyst
  note:  Sequential experiment plan — for each hypothesis: channel, minimum budget, success metric, duration, binary decision rule.
```

## Purpose

Step 19. Designs the concrete experiment sequence for Phase 3:
landing + ads, outbound sequences, content/SEO, community seeding.
For each experiment declares: hypothesis tested, channel, minimum
statistically defensible budget, success metric with numerical
threshold, duration, binary go/no-go rule. Orders the plan to
maximise learning per euro.

## Inspiration

`validation-experiment-plan` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 16, 17, 18
- **Writes:** `19_validation_experiments.md`
- **Upstream:** `validation_hypotheses_analyst`, `channel_economics_modeler`, `ltv_cac_targeter`
- **Downstream:** `tranche_1_budgeter`, `scaling_gate_definer`

## Structured output

```python
class Experiment(BaseModel):
    experiment_id: str
    hypothesis_id: str
    channel: str
    min_budget_eur: float
    success_metric: str
    threshold: str                          # numerical
    duration_days: int
    decision_rule: str                      # binary
    order: int

class ExperimentPlan(BaseModel):
    experiments: list[Experiment]
    total_budget_eur: float
    calendar: str
```

## Prompt shape

- **System:** "Minimum budget = the smallest spend that yields
  statistical power to falsify. Under that, you are not running an
  experiment, you are guessing. Cite the sample size assumption
  explicitly."
- **User:** hypotheses + channel benchmarks + LTV/CAC targets.

## Extension notes

- Sequence experiments so the cheapest / fastest run first — kill
  bad hypotheses before spending on the expensive tests.
