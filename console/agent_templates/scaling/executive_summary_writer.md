---
id: executive_summary_writer
name: executive_summary_writer
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 38
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [financial_business_planner, financial_excel_builder, risk_assessor, gtm_strategist]
produces: pdf
tools: [read_prior_step, write_pdf]
tags: [executive-summary, pdf, one-pager, phase-4]
gate: false
optional: false
---

# executive_summary_writer

## Identity

```yaml
- name:  executive_summary_writer
  queue: hermes-agents
  role:  writer
  note:  Two-page executive summary PDF distilling the entire project into a decision-ready document.
```

## Purpose

Step 38. Distills the entire project into a two-page executive
summary PDF: problem, solution, market size, traction, business
model, unit economics, GTM, team, ask, roadmap. Designed to be the
document a decision-maker reads first — the pitch deck is
narrative, this is dense.

## Inspiration

`executive-summary-pdf` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |
| `write_pdf(sections)` | reportlab | — | — |

## Wiring

- **Reads:** steps 1-37
- **Writes:** `38_executive_summary.pdf`
- **Upstream:** `financial_business_planner`, `financial_excel_builder`, `risk_assessor`, `gtm_strategist`
- **Downstream:** `pitch_deck_designer`

## Structured output

```python
class ExecutiveSummary(BaseModel):
    pdf_path: str                          # 38_executive_summary.pdf
    problem: str
    solution: str
    market_size_eur: str
    traction: str
    business_model: str
    unit_economics: str
    gtm: str
    team: str
    ask: str
    roadmap: str
```

## Prompt shape

- **System:** "Two pages, no more. Every claim references a prior
  step. Author = 'Ironbat Digital LLC'."
- **User:** all prior steps.

## Extension notes

- Follow `office/pdf` skill rules — clickable citations, superscript
  footnotes, professional fonts (Inter/DM Sans).
