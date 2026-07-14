---
id: tech_stack_vendors_analyst
name: tech_stack_vendors_analyst
category: scaling
phase: 4
step: 31
role: analyst
mode: pipeline-stage
depends_on: [platform_areas_architect, data_schema_designer]
produces: markdown_report
tools: [web_search, fetch_url, wide_browse, read_prior_step]
tags: [tech-stack, vendors, cloud, build-vs-buy, phase-4]
gate: false
optional: false
---

# tech_stack_vendors_analyst

## Identity

```yaml
- name:  tech_stack_vendors_analyst
  queue: hermes-agents
  role:  analyst
  note:  Full scaling-stage tech stack — languages, frameworks, cloud, databases, auth, comms, analytics, payments, with vendor comparison and monthly cost projection.
```

## Purpose

Step 31. Selects the scaling-stage stack across every layer:
runtimes, frameworks, cloud provider, databases (transactional +
analytical), auth, communications, observability, analytics,
payments, LLM providers. For each layer: 2-3 vendors compared on
cost, lock-in, SLA, EU compliance. Emits a projected monthly cost
curve at 100 / 1k / 10k users and identifies critical build-vs-buy
decisions.

## Inspiration

`tech-stack-vendors` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `wide_browse(vendors, schema)` | batch browser | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 14, 26, 27 (if any), 28
- **Writes:** `31_tech_stack_vendors.md`
- **Upstream:** `platform_areas_architect`, `data_schema_designer`
- **Downstream:** `financial_business_planner`, `risk_assessor`

## Structured output

```python
class Vendor(BaseModel):
    layer: str
    vendor: str
    monthly_cost_100_eur: float
    monthly_cost_1k_eur: float
    monthly_cost_10k_eur: float
    sla: str
    eu_compliant: bool
    lock_in_notes: str
    sources: list[str]

class TechStackReport(BaseModel):
    vendors: list[Vendor]
    build_vs_buy_decisions: list[str]
    total_monthly_100_eur: float
    total_monthly_1k_eur: float
    total_monthly_10k_eur: float
```

## Prompt shape

- **System:** "Every cost is anchored to the vendor's public
  pricing page. If pricing is 'contact sales', mark it and estimate
  a conservative range."
- **User:** platform-areas + data model + minimal-stack (step 14).

## Extension notes

- The minimal step-14 stack is the starting point — this template
  extends it, not replaces it.
