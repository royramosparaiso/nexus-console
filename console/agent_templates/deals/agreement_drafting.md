---
id: agreement_drafting
name: agreement_drafting
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [contract_templates, clause_library]
tags: [contract, drafting, redlines]
gate: false
optional: false
---

# agreement_drafting

## Identity

```yaml
agents:
  - name: agreement_drafting
    role: writer
    mode: single-shot
    produces: structured_json
    domain: deals
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts contracts from templates with negotiated clauses redlined; flags anything outside pre-approved boundaries.

## Inspiration

Derived from the Business Operations rollout planner — Agreement Drafting cell in the deals × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `contract_templates` | provider-specific | vendor | maybe |
| `clause_library` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Deal terms + contract template.
- **Writes**: Redlined draft + risk flags..
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

- **System**: "You run the Agreement Drafting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
