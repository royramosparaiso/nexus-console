---
id: macro_context_agent
name: macro_context_agent
category: finance
phase: null
step: null
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [get_cpi, get_calendar, get_treasury_curve, get_reference_rates, get_commodity_spot]
tags: [finance, macro, fred, rates, openbb]
gate: false
optional: false
---

# macro_context_agent

## Identity

```yaml
name:  macro_context_agent
queue: hermes-agents
role:  analyst
note:  Pulls macro series and rates; produces a macro-regime brief.
```

## Purpose

Establish the macro backdrop against which the other analysts'
reports are read. Not per-ticker — the same macro brief is reusable
across every symbol analysed on the same day. Cache aggressively.

## Inspiration

- **TradingAgents / News Analyst** — the FRED integration is the
  macro slice of that agent ([news_analyst.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/analysts/news_analyst.py#L13-L67)).
- **OpenBB `economy` + `fixedincome`** — both extensions cover the
  macro data primitives ([economy_router.py](https://github.com/OpenBB-finance/OpenBB/blob/develop/openbb_platform/extensions/economy/openbb_economy/economy_router.py), [fixedincome extension](https://github.com/OpenBB-finance/OpenBB/tree/develop/openbb_platform/extensions/fixedincome/openbb_fixedincome)).

## Tools

| Tool | Backing endpoint | Provider chain | Key? |
| --- | --- | --- | --- |
| `get_cpi(country="united_states")` | `obb.economy.cpi` | `fred → oecd` | fred yes |
| `get_calendar(window_days=14)` | `obb.economy.calendar` | `fmp → tradingeconomics → nasdaq` | yes |
| `get_treasury_curve()` | `obb.fixedincome.government.tcm` | `fmp → fred` | yes |
| `get_reference_rates()` | `obb.fixedincome.rate.sofr / effr` | `fred` | yes |
| `get_commodity_spot(commodity)` | `obb.commodity.price.spot` | `fmp` | yes |

## Wiring

- **Reads from state:** `as_of_date`, optionally `region`
- **Writes to state:** `macro_context` (structured output below)
- **Upstream:** none
- **Downstream:** `bull_bear_debate_pair`, `risk_committee`

**Cache scope:** by `(as_of_date, region)`. If two symbol analyses
run within the same trading day for the same region, the macro brief
should not be recomputed. In-process cache is fine; the reflector
agent doesn't touch this state key.

## Structured output

```python
class MacroContext(BaseModel):
    as_of_date: date
    region: str = "US"
    regime: Literal["expansion", "late_cycle", "contraction", "recovery"]
    inflation_trend: Literal["disinflation", "stable", "reaccelerating"]
    rate_stance: Literal["easing", "hold", "tightening"]
    yield_curve: Literal["steep", "normal", "flat", "inverted"]
    calendar_highlights: list[str]         # e.g. ["FOMC 2026-07-30", "US CPI 2026-07-16"]
    narrative: str                          # 3-5 sentence brief
```

## Prompt shape

- **System:** "You are a macro analyst. You read inflation, growth
  and rates data. You do not comment on individual securities. You
  describe the regime, not your own view of what should happen."
- **User:** interpolates `as_of_date` and `region`.

## Extension notes

- OECD is the natural fallback for `get_cpi` when the region isn't
  US, but coverage lags 1-2 months.
- The commodity slice is optional — include it only if the downstream
  debate references energy or ag exposure. Otherwise it's noise.
