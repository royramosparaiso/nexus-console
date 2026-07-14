---
id: mvp_scoper
name: mvp_scoper
artifact_type: agent
lifecycle: project
category: mvs
phase: 2
step: 13
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [strategic_decision_gate, market_customer_profiler, competitive_analyst]
produces: markdown_report
tools: [read_prior_step]
tags: [mvp, scope, in-scope, out-of-scope, phase-2]
gate: false
optional: false
---

# mvp_scoper

## Identity

```yaml
- name:  mvp_scoper
  queue: hermes-agents
  role:  analyst
  note:  Defines the irreducible MVP scope needed to validate market demand, plus the explicit out-of-scope list.
```

## Purpose

Step 13, the anchor of Phase 2. Produces two lists:
- **In-scope:** the smallest feature set that lets a target buyer
  pay, or a channel generate a qualified lead.
- **Out-of-scope:** everything explicitly deferred to post-Gate 1.

Operates under the constraint that the founder builds at zero
labor cost. Flags only features that require paid external
development or mandatory paid tooling.

## Inspiration

`mvp-scope-definition` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** customer profiles, competitive analysis, gap analysis
- **Writes:** `13_mvp_scope.md`
- **Upstream:** Phase-1 outputs
- **Downstream:** `minimal_tech_stack_cost_estimator`, `functional_specifier`, `product_roadmap_writer`

## Structured output

```python
class Feature(BaseModel):
    name: str
    justification: str                     # which buyer action this unlocks
    depends_on: list[str]                  # other feature names
    external_dev_required: bool
    external_dev_cost_eur: float
    mandatory_paid_tool: str | None

class MvpScope(BaseModel):
    in_scope: list[Feature]
    out_of_scope: list[Feature]
    core_pct_of_final_product: int         # e.g. 80
    total_paid_dev_eur: float
    total_paid_tools_monthly_eur: float
```

## Prompt shape

- **System:** "In-scope means required to validate — not required to
  scale. If removing a feature does not block validation, it is
  out-of-scope."
- **User:** customer profiles + competitor must-haves + intake.

## Extension notes

- Under the IronBat Dev Model the Core represents ~80-90% of the
  eventual product. This field is honest — do not round it to 20% to
  make the founder feel like they still have runway to build.
