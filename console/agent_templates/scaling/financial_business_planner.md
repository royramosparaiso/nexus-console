---
id: financial_business_planner
name: financial_business_planner
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 34
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [gtm_strategist, tech_stack_vendors_analyst, legal_ip_analyst, risk_assessor,
  kpis_okrs_framework_writer]
produces: markdown_report
tools: [read_prior_step]
tags: [business-plan, financials, revenue-model, hiring, phase-4]
gate: false
optional: false
---

# financial_business_planner
## Identity

```yaml
- name:  financial_business_planner
  queue: hermes-agents
  role:  writer
  note:  Narrative business plan — vision, revenue model, unit economics, hiring plan, 3-year P&L narrative.
```

## Purpose

Step 34. Narrative business plan that ties every prior artifact
into a coherent story: vision, problem, solution, market, business
model, revenue model, unit economics from step 18, GTM from step
30, hiring plan for 12 and 24 months, risk register from step 33,
3-year P&L narrative (numeric spreadsheet is step 35).

## Inspiration

`financial-business-plan` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 1-33
- **Writes:** `34_business_plan.md`
- **Upstream:** `gtm_strategist`, `tech_stack_vendors_analyst`, `legal_ip_analyst`, `risk_assessor`, `kpis_okrs_framework_writer`
- **Downstream:** `financial_excel_builder`, `executive_summary_writer`, `pitch_deck_designer`

## Structured output

```python
class BusinessPlan(BaseModel):
    vision: str
    problem: str
    solution: str
    market: str
    business_model: str
    revenue_model: str
    unit_economics: str
    gtm: str
    hiring_plan_12m: list[str]
    hiring_plan_24m: list[str]
    risks: str
    financials_narrative: str
    milestones: list[str]
```

## Prompt shape

- **System:** "Every claim traces to a prior step. If it doesn't,
  remove it."
- **User:** entire pipeline so far.

## Extension notes

- No numbers invented here. Numbers live in step 35.
