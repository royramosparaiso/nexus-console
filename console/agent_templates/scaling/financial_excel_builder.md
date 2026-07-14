---
id: financial_excel_builder
name: financial_excel_builder
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 35
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [financial_business_planner]
produces: xlsx
tools: [read_prior_step, write_xlsx]
tags: [xlsx, financials, projections, sensitivity, phase-4]
gate: false
optional: false
---

# financial_excel_builder

## Identity

```yaml
- name:  financial_excel_builder
  queue: hermes-agents
  role:  analyst
  note:  36-month P&L / cash-flow / balance-sheet workbook with sensitivity and unit-economics dashboard.
```

## Purpose

Step 35. Builds the numerical financial model as an XLSX workbook:
36-month P&L, cash flow, balance sheet, unit economics dashboard,
CAC and LTV rollup, hiring cost stack, cloud cost projection,
sensitivity tables (CAC ±20%, churn ±20%, ARPU ±10%), scenario
switch (conservative / base / stretch).

## Inspiration

`financial-excel` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |
| `write_xlsx(sheets)` | openpyxl | — | — |

## Wiring

- **Reads:** step 34 (+ 8, 17, 18, 30, 31, 32, 33)
- **Writes:** `35_financials.xlsx`
- **Upstream:** `financial_business_planner`
- **Downstream:** `startup_valuation_analyst`, `fundraising_strategist`, `pitch_deck_designer`

## Structured output

```python
class FinancialsBundle(BaseModel):
    workbook_path: str                     # 35_financials.xlsx
    sheets: list[str]                      # P&L, CF, BS, UE, Hiring, Cloud, Sensitivity, Scenarios, Assumptions
    baseline_arr_month_36_eur: float
    baseline_cash_burn_month_36_eur: float
    breakeven_month: int | None
    assumptions_snapshot: dict[str, float]
```

## Prompt shape

- **System:** "Every formula references the Assumptions sheet. No
  hardcoded numbers in P&L cells — one edit in Assumptions must
  propagate."
- **User:** business plan + unit economics.

## Extension notes

- Snapshot Assumptions in the markdown sidecar so reviewers can
  audit without opening the workbook.
