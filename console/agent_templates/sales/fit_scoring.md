---
id: fit_scoring
name: fit_scoring
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: classifier
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_crm, score_accounts]
tags: [scoring, fit, icp]
gate: false
optional: false
---

# fit_scoring

## Identity

```yaml
agents:
  - name: fit_scoring
    role: classifier
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Scores every inbound and mined account against the ICP fit model — 0..100 with dimensional breakdown.

## Inspiration

Derived from the Business Operations rollout planner — Fit Scoring cell in the sales × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `score_accounts` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account record + ICP model.
- **Writes**: Fit score + top 3 gaps + top 3 strengths..
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

- **System**: "You run the Fit Scoring job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
