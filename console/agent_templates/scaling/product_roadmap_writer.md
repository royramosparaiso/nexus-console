---
id: product_roadmap_writer
name: product_roadmap_writer
category: scaling
phase: 4
step: 23
role: writer
mode: pipeline-stage
depends_on: [scaling_gate_definer, mvp_scoper, kpis_okrs_framework_writer]
produces: markdown_report
tools: [read_prior_step]
tags: [roadmap, quarters, milestones, phase-4]
gate: false
optional: false
---

# product_roadmap_writer

## Identity

```yaml
- name:  product_roadmap_writer
  queue: hermes-agents
  role:  writer
  note:  Twelve-month product roadmap broken into quarters, tied to KPIs and out-of-scope items from step 13.
```

## Purpose

Step 23. Converts the deferred out-of-scope list (step 13) plus
validated buyer feedback (Phase 3) into a 12-month roadmap. Groups
work by quarter with theme, deliverables, KPI impact, dependencies
and go-live gate.

## Inspiration

`product-roadmap` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 13, 19-21, 22
- **Writes:** `23_product_roadmap.md`
- **Upstream:** `scaling_gate_definer`, `mvp_scoper`, `kpis_okrs_framework_writer`
- **Downstream:** `functional_specifier`, `platform_areas_architect`

## Structured output

```python
class RoadmapQuarter(BaseModel):
    quarter: str
    theme: str
    deliverables: list[str]
    kpi_impact: list[str]
    dependencies: list[str]
    go_live_gate: str

class ProductRoadmap(BaseModel):
    quarters: list[RoadmapQuarter]
    known_risks: list[str]
```

## Prompt shape

- **System:** "Deliverables must be user-observable. 'Refactor auth
  service' is not a roadmap item — 'SSO for enterprise buyers' is."
- **User:** out-of-scope + KPIs + validation learnings.

## Extension notes

- Quarters after Q2 are directional. Refuse to over-commit — the
  further out, the coarser the deliverables.
