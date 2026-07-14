---
id: data_visualization
name: data_visualization
artifact_type: skill
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [chart_render]
tags: [viz, chart, skill]
gate: false
optional: false
---

# data_visualization

## Identity

```yaml
skills:
  - name: data_visualization
    kind: skill
    produces: structured_json
    domain: intelligence
```

## Purpose

Reusable capability: renders charts (bar, line, sankey, choropleth) from a structured dataset spec.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `chart_render` | provider-specific | vendor | maybe |

## Inputs

Dataset + spec.

## Outputs

Chart image or embed..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
