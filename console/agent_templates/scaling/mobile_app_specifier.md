---
id: mobile_app_specifier
name: mobile_app_specifier
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 27
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [platform_areas_architect]
produces: markdown_report
tools: [read_prior_step]
tags: [mobile, ios, android, pwa, phase-4, optional]
gate: false
optional: true
---

# mobile_app_specifier

## Identity

```yaml
- name:  mobile_app_specifier
  queue: hermes-agents
  role:  writer
  note:  Mobile app specification — only runs when platform_areas_architect flagged mobile as required.
```

## Purpose

Step 27, optional. Runs only when step 26 sets
`mobile_recommended = true`. Specifies the mobile experience:
platforms (native iOS/Android vs PWA vs React Native/Expo), scope
subset relative to the web app, offline strategy, push
notifications, App Store / Play Store submission plan, review-time
buffers, distribution strategy.

## Inspiration

`mobile-app-specification` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** step 26
- **Writes:** `27_mobile_app_spec.md`
- **Upstream:** `platform_areas_architect`
- **Downstream:** `ux_platform_designer`, `tech_stack_vendors_analyst`

## Structured output

```python
class MobileAppSpec(BaseModel):
    approach: Literal["native", "pwa", "react_native", "expo", "flutter"]
    rationale: str
    scope_subset: list[str]
    offline: bool
    push_notifications: bool
    store_submission_plan: str
    review_time_buffer_days: int
    distribution: str
```

## Prompt shape

- **System:** "Native is expensive. Choose PWA unless a hard
  requirement (background location, biometrics, offline-first)
  forces native."
- **User:** platform-areas report.

## Extension notes

- Skipped by the coordinator when `mobile_recommended = false`.
