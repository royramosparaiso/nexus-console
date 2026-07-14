---
id: resource_inventory_analyst
name: resource_inventory_analyst
artifact_type: agent
lifecycle: project
category: mvs
phase: 2
step: 11
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [strategic_decision_gate]
produces: markdown_report
tools: [read_intake, read_prior_step]
tags: [resources, inventory, cap-table, mvs, zero-cost, phase-2]
gate: false
optional: false
---

# resource_inventory_analyst

## Identity

```yaml
- name:  resource_inventory_analyst
  queue: hermes-agents
  role:  analyst
  note:  Maps zero-cost resources already available — founder time, own stack, free-tier tools, network, own capital.
```

## Purpose

Step 11, start of Phase 2. Inventories every resource the founding
team already has at zero incremental cost: founder skills and hours,
own tech stack and IP, free-tier SaaS, strategic network (mentors,
advisors, first-client candidates) and committed founder capital.
Builds the preliminary pre-money cap table and flags critical role
gaps that must close before MVP launch (full hiring plan is
deferred to steps 22 and 34).

## Inspiration

`resource-inventory` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_intake()` | filesystem | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** `intake_questionnaire_docx`
- **Writes:** `11_resource_inventory.md`
- **Upstream:** `strategic_decision_gate`
- **Downstream:** `legal_setup_cost_estimator`, `mvp_scoper`, `tranche_0_budgeter`

## Structured output

```python
class FounderResource(BaseModel):
    founder: str
    skills: list[str]
    hours_per_week: int
    equity_pct: float
    vesting: str
    committed_capital_eur: float

class ExternalResource(BaseModel):
    resource: str
    provider: str
    monthly_cost_eur: float               # 0 = free-tier / already-paid
    critical: bool

class ResourceInventory(BaseModel):
    founders: list[FounderResource]
    external: list[ExternalResource]
    cap_table_premoney: str               # markdown table
    critical_gaps: list[str]              # role or resource gaps blocking MVP
```

## Prompt shape

- **System:** "Zero-cost means zero incremental cash outflow. A
  Google Workspace already paid for personal use is still a real
  cost — flag it, don't zero it."
- **User:** intake.

## Extension notes

- `critical_gaps` is a short list — one line each. The full hiring
  plan comes later.
