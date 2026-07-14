---
id: property_dossier
name: property_dossier
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: analyst
mode: single-shot
depends_on: []
produces: pdf
tools: [cadastre_api, comparables_api, write_pdf]
tags: [property, dossier, real-estate]
gate: false
optional: false
---

# property_dossier

## Identity

```yaml
agents:
  - name: property_dossier
    role: analyst
    mode: single-shot
    produces: pdf
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Compiles per-property dossier: title chain, comparables, rental yield, condition report, neighbourhood brief.

## Inspiration

Derived from the Business Operations rollout planner — Property Dossier cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `cadastre_api` | provider-specific | vendor | maybe |
| `comparables_api` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Address + registry + comparables.
- **Writes**: Property dossier PDF..
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

- **System**: "You run the Property Dossier job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
