---
id: market_study_by_country_analyst
name: market_study_by_country_analyst
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 3
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [market_customer_profiler]
produces: markdown_report
tools: [web_search, fetch_url, get_macro_indicators, read_prior_step]
tags: [market, tam, sam, som, country, geo, phase-1]
gate: false
optional: false
---

# market_study_by_country_analyst

## Identity

```yaml
- name:  market_study_by_country_analyst
  queue: hermes-agents
  role:  analyst
  note:  Analyzes TAM/SAM/SOM, macro factors and multi-factor scoring per country.
```

## Purpose

Step 3. Sizes the market per country using TAM / SAM / SOM,
overlays macro factors (GDP, digital adoption, purchasing power,
regulatory friction) and produces a multi-factor scoring that ranks
target markets. Does not design an expansion plan, regional pricing
or country-specific GTM — those are Phase 4.

## Inspiration

`market-study-by-country` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query, filters)` | Perplexity search | — | — |
| `fetch_url(url)` | http | — | — |
| `get_macro_indicators(country, year)` | worldbank / eurostat / fred | mixed | mixed |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** `02_market_customer_profiles.md`, `intake_questionnaire_docx`
- **Writes:** `03_market_study_by_country.md`
- **Upstream:** `market_customer_profiler`
- **Downstream:** `market_gap_analyst`, `strategic_decision_gate`

## Structured output

```python
class CountryScoring(BaseModel):
    country: str
    iso2: str
    tam_eur: float
    sam_eur: float
    som_eur_year_1: float
    macro_score: float                 # 0-100
    regulatory_friction: Literal["low", "medium", "high"]
    digital_adoption_score: float
    composite_score: float
    rank: int
    notes: str

class MarketStudyReport(BaseModel):
    countries: list[CountryScoring]
    top_3: list[str]                   # ISO2 codes in order
    methodology: str
```

## Prompt shape

- **System:** "You compute TAM top-down and SAM bottom-up, then
  reconcile. If the two disagree by more than 3×, flag the
  discrepancy — do not average silently."
- **User:** the prior steps + intake target-region field.

## Extension notes

- Restrict the scored country list to 6-10 candidates. Scoring 40
  countries produces noise and slows every downstream step.
- Save the raw data (population, penetration rate, price benchmark
  used) alongside the scored table so `financial_business_planner`
  can trace the SOM assumption.
