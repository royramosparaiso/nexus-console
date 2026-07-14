---
id: platform_areas_architect
name: platform_areas_architect
category: scaling
phase: 4
step: 26
role: analyst
mode: pipeline-stage
depends_on: [functional_specifier, user_roles_permissions_writer]
produces: markdown_report
tools: [read_prior_step]
tags: [platform, areas, modules, architecture, phase-4]
gate: false
optional: false
---

# platform_areas_architect

## Identity

```yaml
- name:  platform_areas_architect
  queue: hermes-agents
  role:  analyst
  note:  Decomposes the platform into functional areas (web app, admin, public site, API, background workers, mobile if needed).
```

## Purpose

Step 26. Decomposes the platform into functional areas: main web
app, admin console, public marketing site, API surface, background
workers, notification pipeline, optional mobile. For each area:
users served, owned features, dependencies, external
integrations, security perimeter. Emits a mobile-app
recommendation used to trigger step 27.

## Inspiration

`platform-areas-architecture` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 24, 25
- **Writes:** `26_platform_areas.md`
- **Upstream:** `functional_specifier`, `user_roles_permissions_writer`
- **Downstream:** `mobile_app_specifier` (only if mobile_recommended), `data_schema_designer`, `ux_platform_designer`, `tech_stack_vendors_analyst`

## Structured output

```python
class PlatformArea(BaseModel):
    area: str
    users_served: list[str]
    features: list[str]
    dependencies: list[str]
    external_integrations: list[str]
    security_perimeter: str

class PlatformAreasReport(BaseModel):
    areas: list[PlatformArea]
    mobile_recommended: bool
    mobile_rationale: str
```

## Prompt shape

- **System:** "Do not architect features that are not in the
  roadmap. A speculative admin module is scope creep."
- **User:** functional specs + roles/permissions.

## Extension notes

- If `mobile_recommended = false`, `mobile_app_specifier` is
  skipped by the coordinator.
