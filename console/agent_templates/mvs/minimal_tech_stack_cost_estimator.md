---
id: minimal_tech_stack_cost_estimator
name: minimal_tech_stack_cost_estimator
category: mvs
phase: 2
step: 14
role: analyst
mode: pipeline-stage
depends_on: [mvp_scoper]
produces: markdown_report
tools: [web_search, fetch_url, read_prior_step]
tags: [tech-stack, alive-cost, mvp, tramo-0, phase-2]
gate: false
optional: false
---

# minimal_tech_stack_cost_estimator

## Identity

```yaml
- name:  minimal_tech_stack_cost_estimator
  queue: hermes-agents
  role:  analyst
  note:  Verified monthly 'alive cost' for the validation-stage stack. Every tool traces back to a Core MVP feature.
```

## Purpose

Step 14. Determines the minimal stack to keep the validation-stage
platform alive and reachable during Tramo 0. Under the IronBat dev
model the founder hosts on existing personal infra (Manus AI or
equivalent), so hosting is near zero. Baseline paid stack: Clerk
basic, Gmail Workspace Business, transactional SMTP (Resend/SES),
primary domain, Stripe (usage-based). If the MVP needs a public PWA
or persistent backend, a small paid GCP/Supabase tier is added.
Every tool listed must map 1:1 to a Core feature from step 13.

## Inspiration

`minimal-tech-stack-cost` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** `13_mvp_scope.md`
- **Writes:** `14_minimal_tech_stack.md`
- **Upstream:** `mvp_scoper`
- **Downstream:** `tranche_0_budgeter`

## Structured output

```python
class StackTool(BaseModel):
    tool: str
    tier: str
    monthly_cost_eur: float
    yearly_cost_eur: float
    justification: str                    # which Core feature requires it
    alternative: str | None

class MinimalStackReport(BaseModel):
    tools: list[StackTool]
    alive_cost_monthly_eur: float
    alive_cost_yearly_eur: float
    notes: str
```

## Prompt shape

- **System:** "A tool with no linked Core feature is not part of the
  minimal stack — move it to out-of-scope. Justify every euro."
- **User:** MVP scope + intake dev-model.

## Extension notes

- If the MVP scope changes (step 13 rerun), this template must
  rerun. Otherwise the alive cost silently drifts.
