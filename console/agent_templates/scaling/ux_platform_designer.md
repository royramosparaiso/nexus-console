---
id: ux_platform_designer
name: ux_platform_designer
category: scaling
phase: 4
step: 29
role: writer
mode: pipeline-stage
depends_on: [functional_specifier, platform_areas_architect]
produces: markdown_report
tools: [read_prior_step]
tags: [ux, information-architecture, navigation, states, phase-4]
gate: false
optional: false
---

# ux_platform_designer

## Identity

```yaml
- name:  ux_platform_designer
  queue: hermes-agents
  role:  writer
  note:  Information architecture, navigation model, primary flows and empty/loading/error states.
```

## Purpose

Step 29. Produces information architecture and navigation model,
primary user flows with entry points and success states, empty /
loading / error state catalog, accessibility floor (WCAG AA),
responsive breakpoints. Does not produce pixel mockups — that is a
downstream design team task.

## Inspiration

`ux-platform-design` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 24, 26 (27 if mobile)
- **Writes:** `29_ux_platform.md`
- **Upstream:** `functional_specifier`, `platform_areas_architect`
- **Downstream:** `gtm_strategist`, external design team

## Structured output

```python
class UxFlow(BaseModel):
    flow: str
    entry_points: list[str]
    steps: list[str]
    success_state: str
    error_states: list[str]

class UxDesign(BaseModel):
    information_architecture: str
    navigation_model: str
    flows: list[UxFlow]
    empty_loading_error_catalog: list[str]
    a11y_floor: Literal["WCAG_AA"]
    breakpoints: list[str]
```

## Prompt shape

- **System:** "Every flow has an empty state, a loading state and
  an error state — if not defined here, the frontend will invent
  bad ones."
- **User:** functional specs + platform areas.

## Extension notes

- If step 27 ran, add a `mobile_adaptations` section.
