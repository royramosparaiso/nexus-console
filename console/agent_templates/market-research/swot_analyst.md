---
id: swot_analyst
name: swot_analyst
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 6
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [market_problem_analyst, market_customer_profiler, market_study_by_country_analyst,
  market_trends_timing_analyst, competitive_analyst]
produces: markdown_report
tools: [read_prior_step]
tags: [swot, dafo, synthesis, phase-1]
gate: false
optional: false
---

# swot_analyst

## Identity

```yaml
- name:  swot_analyst
  queue: hermes-agents
  role:  analyst
  note:  Consolidates prior Phase-1 research into a SWOT / DAFO matrix with cross strategies (SO/WO/ST/WT).
```

## Purpose

Step 6. Reads the outputs of steps 1-5 and produces a SWOT: internal
Strengths & Weaknesses, external Opportunities & Threats. Adds a
priority matrix and the four cross strategies (SO, WO, ST, WT). Does
no new research — pure synthesis.

## Inspiration

`swot-analysis` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 1-5 outputs
- **Writes:** `06_swot_analysis.md`
- **Upstream:** all Phase-1 research templates
- **Downstream:** `market_gap_analyst`, `strategic_decision_gate`, `risk_assessor`

## Structured output

```python
class SwotMatrix(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]
    so_strategies: list[str]
    wo_strategies: list[str]
    st_strategies: list[str]
    wt_strategies: list[str]
    priority_matrix: str                 # markdown table
```

## Prompt shape

- **System:** "You do not invent new data. Every SWOT item cites the
  prior step it came from. If nothing supports a claim, drop it."
- **User:** paths to steps 1-5 output files.

## Extension notes

- If the founder disagrees with a Weakness, keep it. The SWOT is not
  a sales document.
