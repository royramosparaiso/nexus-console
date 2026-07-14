---
id: gtm_strategist
name: gtm_strategist
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 30
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [scaling_gate_definer, market_customer_profiler, competitive_analyst,
  channel_economics_modeler, ux_platform_designer]
produces: markdown_report
tools: [read_prior_step]
tags: [gtm, go-to-market, launch, motion, phase-4]
gate: false
optional: false
---

# gtm_strategist

## Identity

```yaml
- name:  gtm_strategist
  queue: hermes-agents
  role:  writer
  note:  Go-to-market plan — positioning, ICP, primary motion, launch sequence, first 90 days.
```

## Purpose

Step 30. Full go-to-market plan built on validated Phase-3
learnings: positioning statement, ICP, primary sales/marketing
motion (PLG, outbound, partner, hybrid), launch sequence (soft ->
public -> partner), first-90-days playbook, activation funnel,
partner strategy, PR angles.

## Inspiration

`gtm-strategy` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 2, 5, 17, 21, 29
- **Writes:** `30_gtm_strategy.md`
- **Upstream:** `scaling_gate_definer` (PASS required), Phase-1 templates, `channel_economics_modeler`
- **Downstream:** `financial_business_planner`, `executive_summary_writer`

## Structured output

```python
class GtmPlan(BaseModel):
    positioning: str
    icp: str
    primary_motion: Literal["plg", "outbound", "partner", "hybrid"]
    motion_rationale: str
    launch_sequence: list[str]
    first_90_days: list[str]
    activation_funnel: str
    partner_strategy: str
    pr_angles: list[str]
```

## Prompt shape

- **System:** "The primary motion is what pays for itself. Choose
  the one your Phase-3 experiments validated, not the one you find
  more fun."
- **User:** validation outputs + channel benchmarks + UX plan.

## Extension notes

- Refuses when `21_scaling_gate.verdict != "PASS"`.
