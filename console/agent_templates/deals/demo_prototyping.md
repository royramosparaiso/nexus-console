---
id: demo_prototyping
name: demo_prototyping
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, product_surface_index]
tags: [demo, prep]
gate: false
optional: false
---

# demo_prototyping

## Identity

```yaml
agents:
  - name: demo_prototyping
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Builds a bespoke-demo plan for a target account: which product surfaces to open, data to preload, questions to ask, wow moments.

## Inspiration

Derived from the Business Operations rollout planner — Demo Prototyping cell in the deals × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `product_surface_index` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account brief + product surfaces.
- **Writes**: Demo plan..
- **Upstream**: signals or artefacts from foundation-stage cards in the same domain.
- **Downstream**: consumed by orchestration-stage cards or the human operator.

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the Demo Prototyping job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
