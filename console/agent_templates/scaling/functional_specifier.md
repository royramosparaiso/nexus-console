---
id: functional_specifier
name: functional_specifier
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 24
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [product_roadmap_writer]
produces: markdown_report
tools: [read_prior_step]
tags: [functional-spec, user-stories, acceptance, phase-4]
gate: false
optional: false
---

# functional_specifier

## Identity

```yaml
- name:  functional_specifier
  queue: hermes-agents
  role:  writer
  note:  Detailed functional specifications for Q1 roadmap deliverables — user stories, acceptance criteria, edge cases.
```

## Purpose

Step 24. Expands Q1 roadmap deliverables into buildable
specifications: user stories with acceptance criteria, business
rules, edge cases, non-functional requirements (perf, availability,
security floor), open questions. Q2+ deliverables get outline-level
specs only.

## Inspiration

`functional-specifications` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** step 23
- **Writes:** `24_functional_specs.md`
- **Upstream:** `product_roadmap_writer`
- **Downstream:** `data_schema_designer`, `platform_areas_architect`, `ux_platform_designer`

## Structured output

```python
class UserStory(BaseModel):
    story_id: str
    persona: str
    story: str
    acceptance_criteria: list[str]
    edge_cases: list[str]
    non_functional: dict[str, str]         # e.g. {"perf": "p95 < 300ms"}
    open_questions: list[str]

class FunctionalSpecs(BaseModel):
    q1_stories: list[UserStory]
    q2_plus_outlines: list[str]
```

## Prompt shape

- **System:** "Every acceptance criterion is testable. 'Feels fast'
  is not a criterion — 'p95 < 300ms under 100 concurrent users' is."
- **User:** Q1 deliverables + personas.

## Extension notes

- Open questions are legitimate — they become the input for step
  19-style micro-experiments during Phase 4.
