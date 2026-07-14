---
id: kpis_okrs_framework_writer
name: kpis_okrs_framework_writer
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 22
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [scaling_gate_definer]
produces: markdown_report
tools: [read_prior_step]
tags: [kpi, okr, north-star, metrics, phase-4]
gate: false
optional: false
---

# kpis_okrs_framework_writer

## Identity

```yaml
- name:  kpis_okrs_framework_writer
  queue: hermes-agents
  role:  writer
  note:  Defines the north-star metric, top-of-tree KPIs, Q1-Q4 OKRs and reporting cadence. Refuses to run unless Gate 1 = PASS.
```

## Purpose

Step 22, first template of Phase 4. Defines the operational
measurement framework: one north-star metric, 3-5 top-of-tree KPIs
(activation, retention, revenue, efficiency, quality) and four
quarters of OKRs with measurable key results. Sets reporting
cadence (weekly ops review, monthly board update).

## Inspiration

`kpis-okrs-framework` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 8, 18, 21
- **Writes:** `22_kpis_okrs.md`
- **Upstream:** `scaling_gate_definer` (PASS required)
- **Downstream:** `financial_business_planner`, `product_roadmap_writer`

## Structured output

```python
class Kpi(BaseModel):
    kpi: str
    definition: str
    target_q1: str
    target_q4: str
    owner: str

class Okr(BaseModel):
    quarter: str                           # Q1..Q4
    objective: str
    key_results: list[str]

class KpiOkrFramework(BaseModel):
    north_star: str
    kpis: list[Kpi]
    okrs: list[Okr]
    reporting_cadence: str
```

## Prompt shape

- **System:** "The north-star metric captures the value the product
  delivers, not the money it makes. Revenue is a lagging KPI, not a
  north star."
- **User:** Gate-1 outputs.

## Extension notes

- Refuse to run when `21_scaling_gate.verdict != "PASS"`. This is
  the invariant enforced by all Phase-4 templates.
