---
id: market_problem_analyst
name: market_problem_analyst
category: market-research
phase: 1
step: 1
role: analyst
mode: pipeline-stage
depends_on: [project_intake_facilitator]
produces: markdown_report
tools: [web_search, fetch_url, read_intake]
tags: [market, problem, pain-points, phase-1]
gate: false
optional: false
---

# market_problem_analyst

## Identity

```yaml
- name:  market_problem_analyst
  queue: hermes-agents
  role:  analyst
  note:  Identifies market problems, unmet demands and frictions with verifiable sources.
```

## Purpose

Step 1 of the pipeline. Documents the market problem the project
addresses, with verifiable citations. Distinguishes symptoms from
root causes, quantifies pain where possible (frequency, cost of the
problem, workarounds), and maps existing solutions with their gaps.
Does not analyse competitors, customer profiles, TAM/SAM/SOM or GTM
— those are separate steps.

## Inspiration

`market-problem-analysis` skill (user library).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query, filters)` | Perplexity search | — | — |
| `fetch_url(url)` | http | — | — |
| `read_intake()` | filesystem: `intake_questionnaire_docx` | — | — |

## Wiring

- **Reads:** `intake_questionnaire_docx`
- **Writes:** `01_market_problem_analysis.md`
- **Upstream:** `project_intake_facilitator`
- **Downstream:** `market_customer_profiler`, `market_gap_analyst`, `swot_analyst`

## Structured output

```python
class MarketProblem(BaseModel):
    problem_id: str
    description: str
    affected_segments: list[str]
    frequency: Literal["daily", "weekly", "monthly", "occasional"]
    quantified_cost: str | None       # e.g. "€2-4k/year per SMB"
    existing_workarounds: list[str]
    gaps_in_workarounds: list[str]
    sources: list[str]                # URLs

class MarketProblemReport(BaseModel):
    problems: list[MarketProblem]
    ranked_by_severity: list[str]     # problem_ids in priority order
```

## Prompt shape

- **System:** "You are a market-problem analyst. Every claim you make
  is backed by a URL. If you cannot find a source for a claim, drop
  the claim — do not fabricate. Distinguish symptoms from root
  causes."
- **User:** interpolates the intake questionnaire content and the
  founder's problem statement.

## Extension notes

- Anchor at least one source per quantified cost claim. Unquantified
  pain is fine to include but must be labelled as "qualitative".
- Feed the ranked list into `market_gap_analyst` (step 9) — the gap
  analysis relies on knowing which problems matter most.
