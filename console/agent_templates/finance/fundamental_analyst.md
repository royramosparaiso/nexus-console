---
id: fundamental_analyst
name: fundamental_analyst
artifact_type: agent
lifecycle: none
category: finance
phase: null
step: null
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [get_income, get_balance, get_cashflow, get_estimates, get_recent_filings,
  get_insider_trading]
tags: [finance, fundamentals, equity, filings, openbb, sec-edgar]
gate: false
optional: false
---

# fundamental_analyst

## Identity

```yaml
name:  fundamental_analyst
queue: hermes-agents
role:  analyst
note:  Reads financials, filings and analyst estimates; produces a fundamentals brief.
```

## Purpose

Pull the last 4-8 quarters of income statement, balance sheet and
cash flow, cross-reference with recent SEC filings and analyst
consensus, and write a fundamentals brief. This is the "read the
numbers" role — separate from macro context and separate from the
tape.

## Inspiration

- **TradingAgents / Fundamentals Analyst** ([fundamentals_analyst.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/analysts/fundamentals_analyst.py#L13-L67)).
- **OpenBB `equity.fundamental`** ([equity extension](https://github.com/OpenBB-finance/OpenBB/tree/develop/openbb_platform/extensions/equity/openbb_equity)) and **`regulators.sec`** ([sec_router.py](https://github.com/OpenBB-finance/OpenBB/blob/develop/openbb_platform/extensions/regulators/openbb_regulators/sec/sec_router.py)) — the latter is free (no API key), which makes this template runnable on a fresh install.

## Tools

| Tool | Backing endpoint | Provider chain | Key? |
| --- | --- | --- | --- |
| `get_income(symbol, periods=8)` | `obb.equity.fundamental.income` | `fmp → intrinio → yfinance` | fmp / intrinio yes |
| `get_balance(symbol, periods=8)` | `obb.equity.fundamental.balance` | same | same |
| `get_cashflow(symbol, periods=8)` | `obb.equity.fundamental.cash` | same | same |
| `get_estimates(symbol)` | `obb.equity.estimates.consensus` | `fmp` | yes |
| `get_recent_filings(symbol, form_types=["10-K","10-Q","8-K"])` | `obb.regulators.sec.filing_headers` | SEC EDGAR | **no** |
| `get_insider_trading(symbol)` | `obb.equity.ownership.insider_trading` | `fmp / sec` | mixed |

## Wiring

- **Reads from state:** `symbol`, `as_of_date`
- **Writes to state:** `fundamentals_report` (structured output below)
- **Upstream:** none (parallel to `market_research_analyst`)
- **Downstream:** `bull_bear_debate_pair`

## Structured output

```python
class FundamentalReport(BaseModel):
    symbol: str
    as_of_date: date
    growth: dict[Literal["revenue", "eps", "fcf"], float]   # YoY %
    profitability: dict[Literal["gross", "operating", "net"], float]
    leverage: Literal["low", "moderate", "elevated", "high"]
    consensus: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"] | None
    recent_filings: list[str]                                # e.g. ["10-Q 2026-Q1", "8-K 2026-04-14"]
    insider_signal: Literal["accumulating", "distributing", "neutral"] | None
    narrative: str                                           # 4-8 sentence brief
```

## Prompt shape

- **System:** "You are a fundamentals analyst. You read financial
  statements, analyst consensus and recent filings. You do not
  comment on price action or macro conditions. If a data point is
  missing, say so explicitly — do not fabricate."
- **User:** interpolates `symbol`, `as_of_date`, and any relevant
  memory-log entries.

## Extension notes

- The SEC EDGAR provider is free and covers filings + institutional
  holdings. If you can only afford one paid provider, FMP is the one
  that unlocks the most downstream endpoints in this template.
- `get_insider_trading` uses SEC Form 4 data via EDGAR when FMP is
  absent — the report should be usable even on a keyless install,
  just with narrower fields populated.
