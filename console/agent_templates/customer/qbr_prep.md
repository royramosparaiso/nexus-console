---
id: qbr_prep
name: qbr_prep
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: pptx
tools: [read_usage, write_pptx]
tags: [qbr, csm]
gate: false
optional: false
---

# qbr_prep

## Identity

```yaml
agents:
  - name: qbr_prep
    role: writer
    mode: single-shot
    produces: pptx
    domain: customer
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Prepares the QBR deck: usage trends, wins, risks, roadmap ask, exec asks.

## Inspiration

Derived from the Business Operations rollout planner — QBR Prep cell in the customer × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_usage` | provider-specific | vendor | maybe |
| `write_pptx` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Customer usage + notes + roadmap.
- **Writes**: QBR deck..
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

- **System**: "You run the QBR Prep job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
