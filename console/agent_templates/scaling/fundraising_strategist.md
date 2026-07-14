---
id: fundraising_strategist
name: fundraising_strategist
category: scaling
phase: 4
step: 37
role: writer
mode: pipeline-stage
depends_on: [startup_valuation_analyst]
produces: markdown_report
tools: [web_search, fetch_url, read_prior_step]
tags: [fundraising, round, investors, term-sheet, phase-4, optional]
gate: false
optional: true
---

# fundraising_strategist

## Identity

```yaml
- name:  fundraising_strategist
  queue: hermes-agents
  role:  writer
  note:  Fundraising plan — round structure, target investors, use of funds, milestones, roadshow calendar.
```

## Purpose

Step 37, optional. Companion to `startup_valuation_analyst`.
Designs the round: type (SAFE / convertible / equity), target
amount, valuation cap, use of funds, milestones the round unlocks,
investor targeting (angels, seed funds, family offices, strategic),
roadshow calendar, KPIs to hit before term sheets.

## Inspiration

`fundraising-strategy` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** step 36 (+ 33, 34, 35)
- **Writes:** `37_fundraising.md`
- **Upstream:** `startup_valuation_analyst`
- **Downstream:** `pitch_deck_designer`

## Structured output

```python
class InvestorTarget(BaseModel):
    name: str
    type: Literal["angel", "seed_fund", "family_office", "strategic", "grant"]
    thesis_fit: str
    ticket_range_eur: str
    priority: int

class FundraisingPlan(BaseModel):
    round_type: Literal["safe", "convertible", "equity_seed", "equity_series_a"]
    target_amount_eur: float
    valuation_cap_eur: float | None
    use_of_funds: dict[str, float]
    milestones_unlocked: list[str]
    investor_targets: list[InvestorTarget]
    roadshow_calendar: str
    prereq_kpis: list[str]
```

## Prompt shape

- **System:** "Round type follows stage and traction, not founder
  preference. A pre-revenue startup does not run a Series A."
- **User:** valuation + business plan + risks.

## Extension notes

- Skipped when founder does not intend to raise (mirrors step 36).
