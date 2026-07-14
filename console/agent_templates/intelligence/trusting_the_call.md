---
id: trusting_the_call
name: trusting_the_call
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: judge
mode: single-shot
depends_on: []
produces: decision
tools: [read_prior_step]
tags: [decision, judgement, analyst-led]
gate: false
optional: false
---

# trusting_the_call

## Identity

```yaml
agents:
  - name: trusting_the_call
    role: judge
    mode: single-shot
    produces: decision
    domain: intelligence
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Analyst-led. Reviews an outsized recommendation, checks reasoning against base rates and known biases, calls the shot.

## Inspiration

Derived from the Business Operations rollout planner — Trusting the Call cell in the intelligence × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Recommendation + supporting evidence.
- **Writes**: Go/hold/re-run decision..
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

- **System**: "You run the Trusting the Call job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
