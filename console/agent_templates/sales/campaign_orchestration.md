---
id: campaign_orchestration
name: campaign_orchestration
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: coordinator
mode: event-driven
depends_on: []
produces: decision
tools: [read_outbound_metrics, mutate_sequence]
tags: [orchestration, campaign, bandit]
gate: false
optional: false
---

# campaign_orchestration

## Identity

```yaml
agents:
  - name: campaign_orchestration
    role: coordinator
    mode: event-driven
    produces: decision
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Watches campaign performance, kills bad variants, promotes winners, re-slots contacts across sequences.

## Inspiration

Derived from the Business Operations rollout planner — Campaign Orchestration cell in the sales × 4-orchestrate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_outbound_metrics` | provider-specific | vendor | maybe |
| `mutate_sequence` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Sequence performance metrics.
- **Writes**: Sequence-mutation decisions on the outbound bus..
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

- **System**: "You run the Campaign Orchestration job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
