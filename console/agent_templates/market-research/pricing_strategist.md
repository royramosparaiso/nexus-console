---
id: pricing_strategist
name: pricing_strategist
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 8
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [competitive_analyst, market_study_by_country_analyst, brand_identity_writer]
produces: markdown_report
tools: [web_search, fetch_url, wide_browse, read_prior_step]
tags: [pricing, monetization, tiers, elasticity, phase-1]
gate: false
optional: false
---

# pricing_strategist

## Identity

```yaml
- name:  pricing_strategist
  queue: hermes-agents
  role:  analyst
  note:  Designs pricing model, tiers, packaging and regional adjustments backed by willingness-to-pay research.
```

## Purpose

Step 8. Researches sector pricing models, price elasticity per
region, willingness-to-pay benchmarks. Outputs tiered pricing with
packaging, regional discounts and a monetisation strategy. Feeds
`ltv_cac_targeter` (step 18) with realistic ARPU numbers.

## Inspiration

`pricing-strategy` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `wide_browse(competitor_pricing_urls, schema)` | batch browser | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** `05_competitive_analysis.md`, `03_market_study_by_country.md`, `07_brand_identity_kit.md`
- **Writes:** `08_pricing_strategy.md`
- **Upstream:** `brand_identity_writer`
- **Downstream:** `market_gap_analyst`, `ltv_cac_targeter`, `financial_business_planner`

## Structured output

```python
class PricingTier(BaseModel):
    name: str
    target_segment: str
    monthly_price_eur: float
    annual_price_eur: float | None
    included_features: list[str]
    limits: dict[str, str]

class RegionalAdjustment(BaseModel):
    country: str
    discount_pct: float
    rationale: str

class PricingReport(BaseModel):
    model: Literal["flat", "tiered", "usage_based", "hybrid", "seat_based", "freemium"]
    tiers: list[PricingTier]
    regional: list[RegionalAdjustment]
    willingness_to_pay: dict[str, float]  # segment -> monthly EUR
```

## Prompt shape

- **System:** "You anchor every price on a documented WTP benchmark
  from a comparable product. Prices with no anchor go in a
  `speculative` list, not in the recommendation."
- **User:** competitors + country scoring + brand positioning.

## Extension notes

- Freemium is a marketing lever, not a pricing model. If you
  recommend freemium, spell out the paid conversion assumption
  numerically.
