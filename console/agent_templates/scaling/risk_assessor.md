---
id: risk_assessor
name: risk_assessor
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 33
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [data_schema_designer, tech_stack_vendors_analyst, legal_ip_analyst]
produces: markdown_report
tools: [read_prior_step]
tags: [risk, mitigation, matrix, dependencies, phase-4]
gate: false
optional: false
---

# risk_assessor

## Identity

```yaml
- name:  risk_assessor
  queue: hermes-agents
  role:  analyst
  note:  Risk register — probability × impact scored, per category, with mitigation, owner and dependencies.
```

## Purpose

Step 33. Consolidates market, product, tech, legal, financial and
team risks into a single register. Each entry: description,
category, probability (L/M/H), impact (L/M/H), score, mitigation,
owner, dependency template ids. Emits the top-5 that require
immediate mitigation action.

## Inspiration

`risk-assessment-mitigation` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 6, 28, 31, 32
- **Writes:** `33_risk_register.md`
- **Upstream:** `data_schema_designer`, `tech_stack_vendors_analyst`, `legal_ip_analyst`
- **Downstream:** `financial_business_planner`, `executive_summary_writer`

## Structured output

```python
class Risk(BaseModel):
    risk_id: str
    description: str
    category: Literal["market", "product", "tech", "legal", "financial", "team"]
    probability: Literal["L", "M", "H"]
    impact: Literal["L", "M", "H"]
    score: int                             # e.g. 1..9
    mitigation: str
    owner: str
    depends_on: list[str]

class RiskRegister(BaseModel):
    risks: list[Risk]
    top_5_ids: list[str]
```

## Prompt shape

- **System:** "A risk with no owner is not a risk, it is a wish.
  Every entry has an owner, even if the owner is the founder."
- **User:** SWOT + data model + stack + legal.

## Extension notes

- Score = probability_num × impact_num (each 1/2/3). Sort desc.
