---
id: validation_hypotheses_analyst
name: validation_hypotheses_analyst
artifact_type: agent
lifecycle: project
category: validation
phase: 3
step: 16
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [strategic_decision_gate, market_customer_profiler, competitive_analyst,
  pricing_strategist, market_gap_analyst]
produces: markdown_report
tools: [read_prior_step]
tags: [hypothesis, validation, segment-channel-message, phase-3]
gate: false
optional: false
---

# validation_hypotheses_analyst

## Identity

```yaml
- name:  validation_hypotheses_analyst
  queue: hermes-agents
  role:  analyst
  note:  Ranked backlog of market-validation hypotheses as segment × channel × message triplets with binary success/falsification.
```

## Purpose

Step 16, start of Phase 3. Inherits hypothesis seeds from step 10
and enriches them with steps 2, 5, 8, 9. Every hypothesis is a
`segment × channel × message` triplet with a binary success
criterion and a falsification condition. Output feeds step 19
(experiment design).

## Inspiration

`validation-hypotheses` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 2, 5, 8, 9, 10
- **Writes:** `16_validation_hypotheses.md`
- **Upstream:** `strategic_decision_gate`, Phase-1 templates
- **Downstream:** `channel_economics_modeler`, `validation_experiment_designer`

## Structured output

```python
class Hypothesis(BaseModel):
    hypothesis_id: str
    segment: str
    channel: str
    message: str
    success_criterion: str                 # e.g. "≥3% signup CVR"
    falsification_condition: str
    rank: int
    priority_score: float

class HypothesisBacklog(BaseModel):
    hypotheses: list[Hypothesis]
    top_5_ids: list[str]
```

## Prompt shape

- **System:** "Every hypothesis is falsifiable. If you cannot state
  a numerical threshold that would kill the hypothesis, it is not a
  hypothesis — it is a wish."
- **User:** prior step outputs.

## Extension notes

- 12-20 hypotheses is the useful range. Step 19 will run only the
  top 5-8.
