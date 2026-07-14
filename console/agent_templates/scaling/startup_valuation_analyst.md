---
id: startup_valuation_analyst
name: startup_valuation_analyst
category: scaling
phase: 4
step: 36
role: analyst
mode: pipeline-stage
depends_on: [financial_excel_builder]
produces: markdown_report
tools: [web_search, fetch_url, read_prior_step]
tags: [valuation, comparables, dcf, berkus, scorecard, phase-4, optional]
gate: false
optional: true
---

# startup_valuation_analyst

## Identity

```yaml
- name:  startup_valuation_analyst
  queue: hermes-agents
  role:  analyst
  note:  Multi-method valuation — comparables, Berkus, scorecard, DCF — only runs if founder decides to fundraise.
```

## Purpose

Step 36, optional. Runs only if the founder decides to fundraise
post-Gate 1. Produces a defensible valuation range using multiple
methods (comparable transactions, Berkus, scorecard, risk-adjusted
DCF) with the assumption sheet made explicit and the range
triangulated across methods.

## Inspiration

`startup-valuation` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** step 35 (+ 8, 18, 30, 33, 34)
- **Writes:** `36_valuation.md`
- **Upstream:** `financial_excel_builder`
- **Downstream:** `fundraising_strategist`, `pitch_deck_designer`

## Structured output

```python
class ValuationMethod(BaseModel):
    method: Literal["comparables", "berkus", "scorecard", "dcf"]
    low_eur: float
    mid_eur: float
    high_eur: float
    key_assumption: str
    sources: list[str]

class ValuationReport(BaseModel):
    methods: list[ValuationMethod]
    triangulated_low_eur: float
    triangulated_mid_eur: float
    triangulated_high_eur: float
    narrative: str
```

## Prompt shape

- **System:** "A single-method valuation is not a valuation. Triangulate."
- **User:** financials + comparable transactions.

## Extension notes

- Skipped by the coordinator when the founder does not intend to
  raise.
