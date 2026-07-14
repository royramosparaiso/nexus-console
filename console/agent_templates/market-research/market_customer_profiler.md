---
id: market_customer_profiler
name: market_customer_profiler
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 2
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [market_problem_analyst]
produces: markdown_report
tools: [web_search, fetch_url, read_prior_step]
tags: [market, customer, personas, segmentation, phase-1]
gate: false
optional: false
---

# market_customer_profiler

## Identity

```yaml
- name:  market_customer_profiler
  queue: hermes-agents
  role:  analyst
  note:  Builds paying-customer profiles with demographics, motivations, pain points and a priority matrix.
```

## Purpose

Step 2. Defines segments and buyer personas of paying customers,
their demographics, motivations, pain points and buying triggers.
Outputs a priority matrix (attractiveness × accessibility). Does not
analyse competitors, GTM, TAM/SAM/SOM per country or financials.

## Inspiration

`market-customer-profiles` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query, filters)` | Perplexity search | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** `01_market_problem_analysis.md`, `intake_questionnaire_docx`
- **Writes:** `02_market_customer_profiles.md`
- **Upstream:** `market_problem_analyst`
- **Downstream:** `market_study_by_country_analyst`, `validation_hypotheses_analyst`

## Structured output

```python
class BuyerPersona(BaseModel):
    persona_id: str
    segment: str                       # e.g. "SMB retail owner, ES/PT, 10-50 employees"
    demographics: dict[str, str]
    motivations: list[str]
    pain_points: list[str]             # cross-referenced to problem_ids
    buying_triggers: list[str]
    decision_makers: list[str]
    accessibility_score: int           # 1-5
    attractiveness_score: int          # 1-5

class CustomerProfileReport(BaseModel):
    personas: list[BuyerPersona]
    priority_matrix: str               # markdown table
```

## Prompt shape

- **System:** "You define paying customers, not users. If a segment
  can't or won't pay, it belongs in a separate `non_paying_beneficiaries`
  note, not in the priority matrix."
- **User:** the prior step's problems + intake.

## Extension notes

- The priority matrix is the input every downstream step relies on
  for segment selection. Keep it to 3-5 personas max — more and every
  downstream step gets diluted.
