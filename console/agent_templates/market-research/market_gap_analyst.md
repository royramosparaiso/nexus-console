---
id: market_gap_analyst
name: market_gap_analyst
category: market-research
phase: 1
step: 9
role: analyst
mode: pipeline-stage
depends_on: [market_problem_analyst, market_customer_profiler, market_study_by_country_analyst, market_trends_timing_analyst, competitive_analyst, swot_analyst, pricing_strategist]
produces: markdown_report
tools: [read_prior_step]
tags: [gap, white-space, blue-ocean, quadrant, phase-1]
gate: false
optional: false
---

# market_gap_analyst

## Identity

```yaml
- name:  market_gap_analyst
  queue: hermes-agents
  role:  analyst
  note:  Identifies market gaps and empty quadrants by cross-analyzing all Phase-1 outputs.
```

## Purpose

Step 9, final analytical step of Phase 1. Builds quadrant matrices
(price × value, segment × feature, geography × channel, function ×
industry) to surface white spaces and blue-ocean opportunities.
Ranks the resulting opportunities by market size, lack of
competition, willingness to pay and product fit.

## Inspiration

`market-gap-analysis` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** all Phase-1 outputs (steps 1-8)
- **Writes:** `09_market_gap_analysis.md`
- **Upstream:** every Phase-1 template
- **Downstream:** `strategic_decision_gate`, `validation_hypotheses_analyst`

## Structured output

```python
class Quadrant(BaseModel):
    axes: tuple[str, str]
    label: str
    populated_positions: list[str]
    empty_positions: list[str]

class GapOpportunity(BaseModel):
    opportunity_id: str
    description: str
    market_size_eur: float
    competition_intensity: Literal["none", "low", "medium", "high"]
    wtp_evidence: str
    fit_score: int                        # 1-5
    ranked: int

class MarketGapReport(BaseModel):
    quadrants: list[Quadrant]
    opportunities: list[GapOpportunity]
    top_3_by_size: list[str]
    top_3_by_fit: list[str]
```

## Prompt shape

- **System:** "An empty quadrant is a *hypothesis*, not a
  conclusion. If a quadrant is empty because no buyer wants that
  combination, it's not an opportunity — it's an anti-pattern. Say
  so."
- **User:** all Phase-1 output paths.

## Extension notes

- The output feeds `strategic_decision_gate` — keep the top-3 lists
  short and defensible.
