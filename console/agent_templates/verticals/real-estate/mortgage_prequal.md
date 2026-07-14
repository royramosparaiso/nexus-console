---
id: mortgage_prequal
name: mortgage_prequal
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [lender_apis]
tags: [mortgage, prequal, real-estate]
gate: false
optional: false
---

# mortgage_prequal

## Identity

```yaml
agents:
  - name: mortgage_prequal
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Runs a soft mortgage prequal from buyer inputs; recommends lender panel and expected rate bands.

## Inspiration

Derived from the Business Operations rollout planner — Mortgage Pre-Qual cell in the sales × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `lender_apis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Buyer income + credit + savings.
- **Writes**: Prequal memo..
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

- **System**: "You run the Mortgage Pre-Qual job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
