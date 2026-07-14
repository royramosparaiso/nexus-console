---
id: agent_evaluation
name: agent_evaluation
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: judge
mode: single-shot
depends_on: []
produces: structured_json
tools: [eval_runner]
tags: [evals, quality-gate]
gate: false
optional: false
---

# agent_evaluation

## Identity

```yaml
agents:
  - name: agent_evaluation
    role: judge
    mode: single-shot
    produces: structured_json
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Runs eval suites against production agents — regression, adversarial, cost. Emits scorecards and gates promotion.

## Inspiration

Derived from the Business Operations rollout planner — Agent Evaluation cell in the operations × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `eval_runner` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Agent + eval suites.
- **Writes**: Scorecard + promotion gate..
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

- **System**: "You run the Agent Evaluation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
