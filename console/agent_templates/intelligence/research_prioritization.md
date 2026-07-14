---
id: research_prioritization
name: research_prioritization
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 1-foundation
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_notes]
tags: [research-plan, analyst-led]
gate: false
optional: false
---

# research_prioritization

## Identity

```yaml
agents:
  - name: research_prioritization
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Analyst-led. Given open questions, ranks the next 3-5 research targets by decision value and cost to answer.

## Inspiration

Derived from the Business Operations rollout planner — What to Research Next cell in the intelligence × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Question queue.
- **Writes**: Ranked research plan..
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

- **System**: "You run the What to Research Next job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
