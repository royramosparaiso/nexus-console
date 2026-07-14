---
id: dj_booking_pipeline
name: dj_booking_pipeline
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 1
verticals: [nightclub]
role: coordinator
mode: single-shot
depends_on: []
produces: markdown_report
tools: [contract_templates, read_budget]
tags: [dj, booking, nightclub]
gate: false
optional: false
---

# dj_booking_pipeline

## Identity

```yaml
agents:
  - name: dj_booking_pipeline
    role: coordinator
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Plans DJ bookings: shortlist, fee proposals, contract, promo asset request, riders.

## Inspiration

Derived from the Business Operations rollout planner — DJ Booking Pipeline cell in the operations × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `contract_templates` | provider-specific | vendor | maybe |
| `read_budget` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Season plan + budget.
- **Writes**: Booking bundle..
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

- **System**: "You run the DJ Booking Pipeline job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
