---
id: reply_classification
name: reply_classification
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: structured_json
tools: [read_thread]
tags: [reply, classification]
gate: false
optional: false
---

# reply_classification

## Identity

```yaml
agents:
  - name: reply_classification
    role: classifier
    mode: event-driven
    produces: structured_json
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Classifies every reply on outbound threads: interested / not-now / OOO / referral / unsubscribe / question / objection.

## Inspiration

Derived from the Business Operations rollout planner — Reply Classification cell in the deals × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_thread` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Inbound reply.
- **Writes**: Classification + routing decision..
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

- **System**: "You run the Reply Classification job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
