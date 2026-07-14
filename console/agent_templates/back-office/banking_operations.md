---
id: banking_operations
name: banking_operations
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [banking_api, read_ledger]
tags: [banking, treasury, founder-led]
gate: false
optional: false
---

# banking_operations

## Identity

```yaml
agents:
  - name: banking_operations
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led. Drafts wires, account setups, treasury moves for the founder to authorise.

## Inspiration

Derived from the Business Operations rollout planner — Banking cell in the back-office × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `banking_api` | provider-specific | vendor | maybe |
| `read_ledger` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Cash position + payables.
- **Writes**: Banking instructions..
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

- **System**: "You run the Banking job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
