---
id: risk_committee
name: risk_committee
category: finance
phase: null
step: null
role: debater
mode: debate
depends_on: [bull_bear_debate_pair]
produces: structured_json
tools: [get_volatility_stats]
tags: [finance, risk, sizing, committee, portfolio-manager]
gate: false
optional: false
---

# risk_committee

## Identity

```yaml
# Three-role committee — all three register on the queue and take
# turns in a round-robin, gated by the coordinator.
- name:  risk_aggressive
  queue: hermes-agents
  role:  risk
  note:  Argues for the aggressive risk stance (higher position, wider stops).
- name:  risk_conservative
  queue: hermes-agents
  role:  risk
  note:  Argues for the conservative risk stance (smaller position, tighter stops).
- name:  risk_neutral
  queue: hermes-agents
  role:  risk
  note:  Argues the neutral / status-quo risk stance.
```

Then a fourth agent, the **portfolio_manager**, reads the committee
transcript and emits the final `RiskDecision`.

## Purpose

Given an `InvestmentThesis` from the debate stage, decide *how* to
express it — sizing, stop placement, tolerance for drawdown. The
committee is a three-way debate rather than two-way because risk is
not a binary axis; the neutral role prevents the aggressive/
conservative pair from staking out artificial extremes.

## Inspiration

- **TradingAgents / risk_debators + PortfolioManager** ([risk_debators/](https://github.com/TauricResearch/TradingAgents/tree/main/tradingagents/agents/risk_mgmt)). Their setup uses 3 debators + a final judge — same shape as this template.
- **OpenBB `quantitative.performance`** for the historical volatility
  and drawdown numbers the committee cites ([quantitative extension](https://github.com/OpenBB-finance/OpenBB/tree/develop/openbb_platform/extensions/quantitative/openbb_quantitative)).

## Tools

The three debaters have **no tools**. The `portfolio_manager` has
one:

| Tool | Backing endpoint | Provider chain | Key? |
| --- | --- | --- | --- |
| `get_volatility_stats(symbol, window_days=252)` | `obb.quantitative.performance.omega_ratio` + `stats.stdev` | in-Platform | no |

Reason: the debaters should argue from the reports on the table, not
diverge into ad-hoc data fetches. The portfolio_manager needs one
sanity-check tool to ground the final numeric sizing.

## Wiring

- **Reads from state:** `investment_thesis`, `technical_report`,
  `fundamentals_report`, `macro_context`, `risk_history`,
  `risk_turn`, `max_risk_turns` (default 3, one round each)
- **Writes to state:** appends to `risk_history`, then
  `portfolio_manager` writes `risk_decision`
- **Upstream:** `research_judge`
- **Downstream:** `memory_reflector`

### Router pseudocode

```python
def route_risk(state) -> Literal["risk_aggressive", "risk_conservative", "risk_neutral", "portfolio_manager"]:
    if state["risk_turn"] >= state["max_risk_turns"]:
        return "portfolio_manager"
    order = ["risk_aggressive", "risk_conservative", "risk_neutral"]
    return order[state["risk_turn"] % 3]

PATH_MAP = {
    "risk_aggressive":   "risk_aggressive",
    "risk_conservative": "risk_conservative",
    "risk_neutral":      "risk_neutral",
    "portfolio_manager": "portfolio_manager",
}
```

## Structured output

Debater turns are free text. The `portfolio_manager` emits:

```python
class RiskDecision(BaseModel):
    symbol: str
    as_of_date: date
    action: Literal["enter", "add", "trim", "exit", "hold"]
    position_size_pct: float           # 0.0 - 1.0 of the risk budget
    stop_loss_pct: float | None        # e.g. 0.08 for 8%
    target_pct: float | None
    time_stop_days: int | None
    rationale: str                     # 3-6 sentences
    committee_dissent: str             # one sentence naming the strongest opposing view
```

`committee_dissent` mirrors the `dissenting_view` field in
`InvestmentThesis` — same reason: the reflector will later check
whether the dissenter was right.

## Prompt shape

- **System (aggressive):** "You argue for a larger position and wider
  stops. You reference historical volatility and the strength of the
  thesis. You do not argue the thesis itself is right or wrong — you
  argue about sizing."
- **System (conservative):** "You argue for a smaller position and
  tighter stops. You emphasise drawdown tolerance and correlated
  exposures."
- **System (neutral):** "You argue for the mid-book stance. You are
  not a compromise between the other two — you have your own
  position, informed by base-rate reasoning and average
  historical outcomes."
- **System (portfolio_manager):** "You have read the committee's
  turns. Emit a `RiskDecision` with concrete numbers. Preserve the
  strongest dissent in `committee_dissent`."

## Extension notes

- One round (3 turns total) is usually enough. Two rounds only if
  the thesis has high conviction but the reports disagree on
  volatility regime.
- If you have real portfolio state (existing positions, correlation
  matrix), the `portfolio_manager` should read it before emitting the
  decision. That's a deployment concern, not a template one — bind a
  `get_portfolio_state()` tool to the agent in your kernel config.
