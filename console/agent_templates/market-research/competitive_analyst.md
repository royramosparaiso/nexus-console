---
id: competitive_analyst
name: competitive_analyst
category: market-research
phase: 1
step: 5
role: analyst
mode: pipeline-stage
depends_on: [market_customer_profiler]
produces: markdown_report
tools: [web_search, fetch_url, wide_browse, read_prior_step]
tags: [market, competition, positioning, features, pricing, phase-1]
gate: false
optional: false
---

# competitive_analyst

## Identity

```yaml
- name:  competitive_analyst
  queue: hermes-agents
  role:  analyst
  note:  Profiles direct and indirect competitors, compares features and pricing, builds a positioning map.
```

## Purpose

Step 5. Identifies direct and indirect competitors, profiles each
(size, revenue, funding, geo, target segment), compares features
and pricing, builds a positioning map and recommends which features
the project must have. Does not design pricing strategy, brand
positioning, messaging or acquisition channels.

## Inspiration

`competitive-analysis` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `wide_browse(competitor_urls, schema)` | batch browser | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** prior Phase-1 steps
- **Writes:** `05_competitive_analysis.md`
- **Upstream:** `market_customer_profiler`
- **Downstream:** `swot_analyst`, `brand_identity_writer`, `pricing_strategist`, `market_gap_analyst`

## Structured output

```python
class Competitor(BaseModel):
    name: str
    website: str
    positioning: str
    price_range_eur: str
    target_segment: str
    funding_stage: str | None
    strengths: list[str]
    weaknesses: list[str]
    features: dict[str, bool]           # feature name -> present

class CompetitiveReport(BaseModel):
    direct: list[Competitor]
    indirect: list[Competitor]
    positioning_map: str                 # markdown / ascii chart
    must_have_features: list[str]
    differentiators: list[str]
```

## Prompt shape

- **System:** "You compare on the axes buyers care about, not the
  axes founders think matter. If two competitors are identical on the
  buyer's axes and differ only on internal architecture, that is not
  a differentiator."
- **User:** target segments + prior steps.

## Extension notes

- Cap at 10 competitors — 5 direct + 5 indirect. Beyond that, no
  human reads the table.
- Use `wide_browse` to extract pricing pages in parallel when the
  competitor set is >5.
