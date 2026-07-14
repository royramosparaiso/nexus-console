---
id: bottle_service_pricing
name: bottle_service_pricing
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [nightclub]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_reservations, statistical_analysis]
tags: [pricing, bottle-service, nightclub]
gate: false
optional: false
---

# bottle_service_pricing

## Identity

```yaml
agents:
  - name: bottle_service_pricing
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Dynamic pricing recommendations for bottle service by night, promoter, table position — protects floor rate.

## Inspiration

Derived from the Business Operations rollout planner — Bottle Service Pricing cell in the operations × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_reservations` | provider-specific | vendor | maybe |
| `statistical_analysis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: History + reservations.
- **Writes**: Pricing plan per night..
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

- **System**: "You run the Bottle Service Pricing job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
