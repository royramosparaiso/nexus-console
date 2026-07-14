---
id: memory_reflector
name: memory_reflector
category: finance
phase: null
step: null
role: reflector
mode: reflector
depends_on: [risk_committee]
produces: reflection
tools: [get_price_at, append_reflection, list_pending_reflections]
tags: [finance, memory, postmortem, outcome, reflection]
gate: false
optional: false
---

# memory_reflector

## Identity

```yaml
name:  memory_reflector
queue: hermes-agents
role:  reflector
note:  After the outcome window closes, writes a reflection tying the decision to what actually happened.
```

## Purpose

Close the loop. Every other agent in this catalogue writes forward —
reports, debates, decisions. The reflector writes **backward**: it
waits until the outcome window has passed (days / weeks / months
depending on the thesis's `time_horizon`) and then produces a
reflection anchored in the actual price outcome.

This is what makes the memory layer useful over time. Vector-search
over past debates is nearly worthless; a small append-only log of
"we said long with high conviction, the stock fell 12% over the
horizon, the bear's dissent about margin compression was the point
we missed" is genuinely useful.

## Inspiration

- **TradingAgents / Reflection + Memory** ([reflect_and_remember.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/graph/reflection.py) — pending-outcomes queue resolved when real prices come in). The core lesson: **never reflect from the agent's own confidence at decision time**. Only reflect once the outcome is objectively known.

## Tools

| Tool | Backing endpoint | Provider chain | Key? |
| --- | --- | --- | --- |
| `get_price_at(symbol, date)` | `obb.equity.price.historical` | `yfinance → fmp` | yfinance no |
| `append_reflection(entry)` | file system: `memory/reflections/<symbol>.md` | — | — |
| `list_pending_reflections()` | file system scan | — | — |

The reflector is a periodic job, not part of the analysis graph.
Trigger it on a cron (daily 00:15 UTC works). It scans the pending
queue, resolves any whose outcome window has closed, and appends to
the reflection log.

## Wiring

- **Reads from state / disk:** `memory/pending/*.json` (decisions
  waiting on outcome), price data via tool
- **Writes to disk:** `memory/reflections/<symbol>.md` (append-only
  markdown log)
- **Upstream:** the entire pipeline — every `RiskDecision` should
  drop a pending entry to disk with its `as_of_date`, `time_horizon`,
  entry price and stated stance
- **Downstream:** every analyst's prompt loads the last N reflection
  entries for the current symbol as context

## Structured output

```python
class Reflection(BaseModel):
    symbol: str
    decision_date: date
    outcome_date: date
    stance_at_decision: Literal["long", "short", "avoid"]
    conviction_at_decision: Literal["low", "medium", "high"]
    price_at_decision: float
    price_at_outcome: float
    return_pct: float
    outcome_vs_stance: Literal["confirmed", "neutral", "contradicted"]
    dissent_at_decision: str          # copied from InvestmentThesis.dissenting_view
    dissent_was_right: bool
    lesson: str                       # 1-3 sentence takeaway
```

The Markdown log stores one entry per line as a fenced code block
plus a prose "lesson" paragraph — grep-friendly, human-readable,
easy to load into analyst prompts.

## Prompt shape

- **System:** "You are a portfolio postmortem writer. You compare a
  past decision to what actually happened. You do not rewrite
  history — you describe what the record shows. If the dissenter was
  right, say so plainly. If the decision was right for the wrong
  reasons, say so too."
- **User:** interpolates the decision record, the outcome prices,
  and the debate's `dissenting_view` / committee dissent.

## Extension notes

- **Do not** vectorise the reflection log for RAG. It's short — a
  well-used deployment produces maybe 200-500 entries a year per
  operator. Linear scan on symbol is fine. If you must, index by
  symbol + `outcome_vs_stance`.
- The `dissent_was_right` boolean is the single most valuable field
  in the log for improving future runs. Analysts should be shown
  their past dissenters that turned out right as a prompt prefix —
  it's a cheap, honest form of self-correction.
- If you don't have the pending queue on disk yet, the coordinator
  agent should write one entry to `memory/pending/<symbol>-<date>.json`
  every time a `RiskDecision` is produced. The reflector reads that
  directory, not the graph state.
