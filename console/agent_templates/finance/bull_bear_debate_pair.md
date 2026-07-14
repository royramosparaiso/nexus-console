---
id: bull_bear_debate_pair
name: bull_bear_debate_pair
category: finance
phase: null
step: null
role: debater
mode: debate
depends_on: [market_research_analyst, fundamental_analyst, macro_context_agent]
produces: structured_json
tools: []
tags: [finance, debate, thesis, bull, bear, judge]
gate: false
optional: false
---

# bull_bear_debate_pair

## Identity

```yaml
# The pair registers as TWO agents on the queue — the debate is a
# turn-based loop between them, orchestrated by the coordinator.
- name:  bull_debater
  queue: hermes-agents
  role:  debater
  note:  Argues the bull side of an investment thesis over N turns.
- name:  bear_debater
  queue: hermes-agents
  role:  debater
  note:  Argues the bear side of an investment thesis over N turns.
```

## Purpose

Turn the three analyst reports (technical, fundamental, macro) into
an investment thesis by pitting a bull agent against a bear agent
for a fixed number of turns. The output is not "who won" but the
final synthesised thesis after both sides have had their say — the
judge is a separate agent (see `research_judge` at the bottom of this
document).

## Inspiration

- **TradingAgents / Researcher pair + Research Manager** ([bull_researcher.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/researchers/bull_researcher.py) and [bear_researcher.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/researchers/bear_researcher.py)). The critical design lesson from that repo: debate is a **shared counter loop**, not a parallel fan-out. Each participant reads the full transcript and appends one turn.

## Tools

**None.** The debaters do not fetch data. They consume the upstream
analyst reports and each other's turns. This is deliberate: if a
debater had tools it would go on data-gathering tangents instead of
arguing the position.

## Wiring

- **Reads from state:** `technical_report`, `fundamentals_report`,
  `macro_context`, `debate_history` (list of turns), `debate_turn` (int),
  `max_debate_turns` (int, default 6)
- **Writes to state:** appends to `debate_history`, increments `debate_turn`
- **Upstream:** `market_research_analyst`, `fundamental_analyst`, `macro_context_agent`
- **Downstream:** `research_judge` (below) which reads the final
  `debate_history` and emits `InvestmentThesis`

### Router pseudocode

```python
def route_debate(state) -> Literal["bull_debater", "bear_debater", "research_judge"]:
    if state["debate_turn"] >= state["max_debate_turns"]:
        return "research_judge"
    # Bull opens; alternate from there.
    return "bull_debater" if state["debate_turn"] % 2 == 0 else "bear_debater"
```

**Exhaustive PATH_MAP** (do not omit any label — this is the same
invariant TradingAgents enforces on its own conditional edges):

```python
PATH_MAP = {
    "bull_debater":  "bull_debater",
    "bear_debater":  "bear_debater",
    "research_judge": "research_judge",
}
```

## Structured output

The individual debate turn is free text (the LLM is arguing, not
filling a schema). The **final** synthesised object is emitted by
`research_judge` and looks like:

```python
class InvestmentThesis(BaseModel):
    symbol: str
    as_of_date: date
    stance: Literal["long", "short", "avoid"]
    conviction: Literal["low", "medium", "high"]
    time_horizon: Literal["days", "weeks", "months", "quarters"]
    key_supports: list[str]           # 2-4 bullets from the winning side
    key_risks: list[str]              # 2-4 bullets from the losing side
    dissenting_view: str              # 1-2 sentences preserving the loser's core point
    narrative: str                    # 5-10 sentence synthesis
```

The dissenting view is intentional. TradingAgents keeps the loser's
argument in the record; it makes the memory reflector much more
useful because it can later ask "did the losing view actually
materialise?"

## `research_judge` — auxiliary agent

```yaml
name:  research_judge
queue: hermes-agents
role:  judge
note:  Reads the full debate transcript and emits an InvestmentThesis.
```

- **Tools:** none.
- **Structured output:** `InvestmentThesis` above. Use
  `bind_structured` if the provider supports it, degrade to prose
  parsing otherwise.
- **Prompt:** "You have read a debate between a bull and a bear. Your
  job is to synthesise, not to referee. State a stance with a
  conviction level. Preserve the strongest counter-argument in
  `dissenting_view` even if you disagree with it."

## Prompt shape (per debater)

- **System (bull):** "You argue the long case for this symbol. You
  read the three analyst reports and every prior turn of the debate.
  You address the bear's most recent point directly. You do not
  fabricate data — if you need a number, cite which report it came
  from."
- **System (bear):** mirror image.
- **User:** interpolates the three reports plus the running
  transcript. Turn number and total turns are visible so the debater
  can pace itself.

## Extension notes

- Setting `max_debate_turns = 2` degrades to a single exchange — fine
  for cheap sanity checks. `6` is the default. Beyond `10` the LLM
  starts repeating.
- If the pair is doing round-trips of "you're wrong" / "no you're
  wrong" without new information after turn 4, that's a signal to
  strengthen the analyst reports upstream, not to extend the debate.
