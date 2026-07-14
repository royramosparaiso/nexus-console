---
id: proposal_generation
name: proposal_generation
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: pdf
tools: [proposal_templates, proof_matching, write_pdf]
tags: [proposal, pdf]
gate: false
optional: false
---

# proposal_generation

## Identity

```yaml
agents:
  - name: proposal_generation
    role: writer
    mode: single-shot
    produces: pdf
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Assembles a full proposal PDF from a deal record: scope, pricing, timeline, terms, case studies — customised to the buyer.

## Inspiration

Derived from the Business Operations rollout planner — Proposal Generation cell in the deals × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `proposal_templates` | provider-specific | vendor | maybe |
| `proof_matching` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal + proof library.
- **Writes**: Proposal PDF..
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

- **System**: "You run the Proposal Generation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
