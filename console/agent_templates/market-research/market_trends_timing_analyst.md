---
id: market_trends_timing_analyst
name: market_trends_timing_analyst
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 4
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [market_study_by_country_analyst]
produces: markdown_report
tools: [web_search, fetch_url, get_search_trends, get_ma_activity, read_prior_step]
tags: [market, trends, timing, adoption, phase-1]
gate: false
optional: false
---

# market_trends_timing_analyst

## Identity

```yaml
- name:  market_trends_timing_analyst
  queue: hermes-agents
  role:  analyst
  note:  Evaluates whether market timing is favourable — adoption curves, tech trends, investment cycles, demand signals.
```

## Purpose

Step 4. Judges whether the launch window is open, closing, or too
early: adoption curves, tech trends, investment cycles in the
category (M&A, funding volume), demand signals (search interest,
job postings, community activity) and macro conditions.

## Inspiration

`market-trends-timing` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query, filters)` | Perplexity | — | — |
| `get_search_trends(term, geo, window)` | Google Trends / Perplexity | — | — |
| `get_ma_activity(category, year)` | Crunchbase / Perplexity | — | — |
| `fetch_url(url)` | http | — | — |

## Wiring

- **Reads:** prior Phase-1 steps
- **Writes:** `04_market_trends_timing.md`
- **Upstream:** `market_study_by_country_analyst`
- **Downstream:** `strategic_decision_gate`, `swot_analyst`

## Structured output

```python
class TimingSignal(BaseModel):
    signal: str
    direction: Literal["favourable", "neutral", "adverse"]
    strength: Literal["weak", "medium", "strong"]
    sources: list[str]

class TrendsTimingReport(BaseModel):
    signals: list[TimingSignal]
    verdict: Literal["window_open", "closing_fast", "too_early", "too_late"]
    justification: str
```

## Prompt shape

- **System:** "You judge timing, not the idea. A great idea in the
  wrong window still fails. If a category is over-funded and
  saturated, say so — even if the founder is convinced otherwise."
- **User:** category + region + prior signals.

## Extension notes

- Over-funding is a timing signal, not a validation. High investment
  activity can mean the window is closing, not opening.
