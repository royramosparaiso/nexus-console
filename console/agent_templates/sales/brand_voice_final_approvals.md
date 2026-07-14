---
id: brand_voice_final_approvals
name: brand_voice_final_approvals
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 2
verticals: [any]
role: reviewer
mode: single-shot
depends_on: []
produces: decision
tools: [brand_voice_guide, diff]
tags: [review, brand-voice, founder-led]
gate: false
optional: false
---

# brand_voice_final_approvals

## Identity

```yaml
agents:
  - name: brand_voice_final_approvals
    role: reviewer
    mode: single-shot
    produces: decision
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led card. Reviews outbound copy against brand voice and approves or rejects with structured feedback.

## Inspiration

Derived from the Business Operations rollout planner — Brand-Voice & Final Approvals cell in the sales × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `brand_voice_guide` | provider-specific | vendor | maybe |
| `diff` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Sequence draft + brand voice guide.
- **Writes**: Approval decision + inline notes..
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

- **System**: "You run the Brand-Voice & Final Approvals job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
