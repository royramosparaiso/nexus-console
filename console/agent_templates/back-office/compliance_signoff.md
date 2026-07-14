---
id: compliance_signoff
name: compliance_signoff
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
role: reviewer
mode: single-shot
depends_on: []
produces: decision
tools: [policy_check]
tags: [compliance, founder-led]
gate: false
optional: false
---

# compliance_signoff

## Identity

```yaml
agents:
  - name: compliance_signoff
    role: reviewer
    mode: single-shot
    produces: decision
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led. Structured compliance sign-off on releases, contracts, campaigns.

## Inspiration

Derived from the Business Operations rollout planner — Compliance Sign-Off cell in the back-office × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `policy_check` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Item + policy pack.
- **Writes**: Sign-off decision..
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

- **System**: "You run the Compliance Sign-Off job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
