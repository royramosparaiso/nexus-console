# Nexus Agent Templates

Design-time catalogue of reusable agent templates. Each template is a
markdown card that specifies the agent's role, its tools, its
upstream/downstream contracts and structured output — enough that a
kernel operator can register the agent by hand or a generator can
lower it into a concrete `DEFAULT_HERMES_AGENTS`-style entry.

**These are not live seeds.** `DEFAULT_HERMES_AGENTS` in
[`app/models/kernel.py`](../app/models/kernel.py) is the minimal set
the kernel boots with (`planner`, `coordinator`, `worker`,
`embeddings`). The templates here are the next layer up — vertical
recipes an operator can install on top of the base four.

## Inspiration

Two open-source projects were mined for these designs:

- **[TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)**
  — a LangGraph-based multi-agent trading framework. Contribution: the
  *orchestration patterns* — turn-based debate as a shared counter,
  ReAct analysts with per-role tool binding, structured-output judges,
  and long-term memory anchored to real outcomes rather than a vector
  store.
- **[OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB)**
  — the Open Data Platform. Contribution: the *data primitives* — a
  unified provider layer covering equity, fundamentals, macro, options,
  news, filings, plus a native MCP server that exposes the whole
  catalogue as tools without integration code.

The templates split cleanly along that seam: some are **research
agents** wired to OpenBB endpoints, some are **judge/debate agents**
that hold no tools of their own and consume upstream reports, and one
is a **memory reflector** that closes the loop between decisions and
outcomes.

## Template catalogue

| Template | Category | Tools | Structured output | Debate participant? |
| --- | --- | --- | --- | --- |
| [`market_research_analyst`](./market_research_analyst.md) | Research | OpenBB equity, technical, quantitative | `MarketReport` | no |
| [`fundamental_analyst`](./fundamental_analyst.md) | Research | OpenBB equity.fundamental, news, regulators.sec | `FundamentalReport` | no |
| [`macro_context_agent`](./macro_context_agent.md) | Research | OpenBB economy, fixedincome, commodity | `MacroContext` | no |
| [`bull_bear_debate_pair`](./bull_bear_debate_pair.md) | Debate | none (consumes upstream reports) | debate turns → `InvestmentThesis` | yes (2 roles) |
| [`risk_committee`](./risk_committee.md) | Debate | none | debate turns → `RiskDecision` | yes (3 roles) |
| [`memory_reflector`](./memory_reflector.md) | Meta | OpenBB equity.price.historical (for outcome check) | `Reflection` (append to memory log) | no |

## How to consume a template

1. Pick the template that matches your workflow.
2. Read the "Wiring" section — it tells you what state keys the agent
   reads and writes, and which upstream agents it depends on.
3. If you want to install it as a Hermes seed, add an entry to
   `DEFAULT_HERMES_AGENTS` with `name`, `queue`, `role`, `note`
   matching the template's identity block. The template's tools
   section maps 1:1 to the tools you bind to the agent's LLM.
4. Structured output schemas are declared in each template with a
   Pydantic-style block — copy it verbatim into `agents/schemas.py`
   or the equivalent module in your deployment.

## Design invariants across all templates

Borrowed from TradingAgents' orchestration lessons ([analysis
report](../../../tmp/analysis-tradingagents.md), section "Key patterns
to reuse"):

1. **Exhaustive PATH_MAPs.** Any conditional router must enumerate
   every label it can emit — no silent fallthroughs.
2. **Debates as counters, not fan-outs.** N debate rounds are a
   shared `count` variable, not N parallel LLM calls. Each participant
   reads the full history and appends one turn.
3. **Explicit provider fallback.** Data-fetching agents declare a
   provider chain (e.g. `["fmp", "yfinance"]`) — no implicit
   fallback. Every value the agent uses can be traced to the provider
   that returned it.
4. **Structured output with free-text fallback.** Judge/output agents
   always try native structured output first (json_schema /
   response_schema / tool-use) and degrade to prose parsing only on
   providers that lack it. Keeps the downstream contract stable across
   LLM backends.
5. **Long-term memory bound to real outcomes.** The memory reflector
   only records reflections after the outcome is verifiable — never
   from the agent's own confidence at decision time. This keeps
   `past_context` grounded rather than self-referential.

## Not covered here (deliberately)

- **Trading execution.** These templates stop at recommendation /
  decision. Anything that touches a broker API is out of scope for
  Nexus core.
- **PDF report generation.** A downstream template could take
  `InvestmentThesis` + `RiskDecision` + reports and emit a formatted
  document, but that belongs in a separate templates directory
  (rendering, not agentic reasoning).
- **Non-finance verticals.** These six are the finance-domain seed. The
  same design shape (research → debate → judge → memory) generalises
  to legal, medical, engineering-review, etc. — but the tool bindings
  and structured outputs would be different.

## Verification

The templates reference OpenBB endpoints that exist in the current
`develop` branch of
[OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) as of
July 2026. Providers marked "no key required" (yfinance, SEC EDGAR,
CBOE, FINRA, Fama-French) work out of the box; providers marked "key
required" (FMP, FRED, Benzinga) need to be set on
`obb.user.credentials` before the tool can be bound.
