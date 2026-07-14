---
id: adversarial_verification
name: adversarial_verification
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: judge
mode: debate
depends_on: []
produces: decision
tools: [citation_check, counter_search]
tags: [verification, adversarial, quality]
gate: false
optional: false
---

# adversarial_verification

## Identity

```yaml
agents:
  - name: adversarial_verification
    role: judge
    mode: debate
    produces: decision
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Runs an adversarial verifier over research outputs — checks citations, logic, counter-evidence — before shipping.

## Inspiration

Derived from the Business Operations rollout planner — Adversarial Verification cell in the intelligence × 4-orchestrate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `citation_check` | provider-specific | vendor | maybe |
| `counter_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Report draft.
- **Writes**: Verification verdict + edit list..
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

- **System**: "You run the Adversarial Verification job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
