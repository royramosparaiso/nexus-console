---
id: reading_between_lines
name: reading_between_lines
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [web_search, read_signals]
tags: [signals, interpretation, analyst-led]
gate: false
optional: false
---

# reading_between_lines

## Identity

```yaml
agents:
  - name: reading_between_lines
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 2-capture
    autonomy: human-led
```

## Purpose

Analyst-led. Interprets ambiguous signals (org changes, hiring, PR silence) into a working hypothesis about the target.

## Inspiration

Derived from the Business Operations rollout planner — Reading Between the Lines cell in the intelligence × 2-capture × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `read_signals` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Public signals.
- **Writes**: Interpretation memo..
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

- **System**: "You run the Reading Between the Lines job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
