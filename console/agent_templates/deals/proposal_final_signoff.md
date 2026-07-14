---
id: proposal_final_signoff
name: proposal_final_signoff
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: reviewer
mode: single-shot
depends_on: []
produces: decision
tools: [proposal_reader, diff]
tags: [approval, proposal, ae-led]
gate: false
optional: false
---

# proposal_final_signoff

## Identity

```yaml
agents:
  - name: proposal_final_signoff
    role: reviewer
    mode: single-shot
    produces: decision
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Human-led final review of proposals before send — checks pricing, T&C, custom clauses, brand voice.

## Inspiration

Derived from the Business Operations rollout planner — Proposal Final Sign-Off cell in the deals × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `proposal_reader` | provider-specific | vendor | maybe |
| `diff` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Proposal draft.
- **Writes**: Approval + inline redlines..
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

- **System**: "You run the Proposal Final Sign-Off job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
