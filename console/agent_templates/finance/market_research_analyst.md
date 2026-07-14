---
id: market_research_analyst
name: market_research_analyst
category: finance
phase: null
step: null
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [get_price_history, get_indicators, get_performance]
tags: [finance, technical, equity, chart, openbb]
gate: false
optional: false
---

# market_research_analyst

## Identity

```yaml
name:  market_research_analyst
queue: hermes-agents
role:  analyst
note:  Reads OHLCV + technical indicators for a symbol; produces a technical brief.
```

## Purpose

Pull recent price history, compute a small, complementary set of
technical indicators, and write a technical brief that downstream
debate agents can read. This is the "eyes on the tape" role — no
opinion on fundamentals, just what the chart says.

## Inspiration

- **TradingAgents / Market Analyst** — the "pick up to N complementary
  indicators, don't spam every one" heuristic ([market_analyst.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/analysts/market_analyst.py#L12-L93)).
- **OpenBB `technical` extension** — indicator computation without
  reimplementing them ([technical_router.py](https://github.com/OpenBB-finance/OpenBB/blob/develop/openbb_platform/extensions/technical/openbb_technical/technical_router.py)).

## Tools

| Tool | Backing endpoint | Provider chain | Key? |
| --- | --- | --- | --- |
| `get_price_history(symbol, start, end)` | `obb.equity.price.historical` | `fmp → yfinance` | fmp yes |
| `get_indicators(symbol, indicators=[...])` | `obb.technical.ema/macd/bbands/rsi` | in-Platform compute | no |
| `get_performance(symbol, window)` | `obb.quantitative.performance.omega_ratio` (and friends) | in-Platform compute | no |

**Constraint:** at most **6 indicators** per call. Any more and the
LLM starts padding the brief with redundant "the MACD confirms the
EMA which confirms the RSI" prose. Six is the empirical ceiling
TradingAgents also settled on (they cap at 8, but their prompt is
sharper than a fresh install).

## Wiring

- **Reads from state:** `symbol`, `as_of_date`, `asset_type`
- **Writes to state:** `technical_report` (structured output below)
- **Upstream:** none — first analyst in the graph
- **Downstream:** `bull_bear_debate_pair`, `fundamental_analyst`

## Structured output

```python
class TechnicalReport(BaseModel):
    symbol: str
    as_of_date: date
    trend: Literal["up", "down", "sideways"]
    momentum: Literal["strengthening", "weakening", "neutral"]
    volatility_regime: Literal["low", "elevated", "high"]
    key_levels: dict[Literal["support", "resistance"], list[float]]
    indicators_used: list[str]          # names of indicators actually consulted
    narrative: str                       # 3-6 sentence brief
```

Use `bind_structured` if the LLM provider supports json_schema /
response_schema / tool-use, degrade to prose parsing otherwise.

## Prompt shape

- **System:** "You are a technical analyst. You look at price and
  indicator data and describe what the tape is doing. You do not
  express a view on fundamentals, valuation, or narrative. You may
  call at most 6 indicators."
- **User:** interpolates `symbol`, `as_of_date`, `asset_type`, and any
  memory-log entries about this symbol from prior runs (see
  `memory_reflector` template).

## Extension notes

- If you add a new provider to OpenBB (e.g. Polygon), add it as an
  option in the tool's provider chain — do not fall back silently.
- The volatility regime bucket can be replaced by a numeric ATR band
  if a downstream risk agent needs precise numbers.
