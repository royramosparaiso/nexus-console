---
id: pr_press_kit
name: pr_press_kit
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [media_database]
tags: [pr, press, release]
gate: false
optional: false
---

# pr_press_kit

## Identity

```yaml
agents:
  - name: pr_press_kit
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts press releases and pitches for news beats — founder announcements, funding, product launches — with journalist targeting.

## Inspiration

Derived from the Business Operations rollout planner — PR & Press Kit cell in the marketing × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `media_database` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: News beat + product docs.
- **Writes**: Press draft + journalist list..
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

- **System**: "You run the PR & Press Kit job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
