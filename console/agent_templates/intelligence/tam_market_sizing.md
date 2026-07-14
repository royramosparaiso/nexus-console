---
id: tam_market_sizing
name: tam_market_sizing
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [web_search, statistical_analysis]
tags: [tam, market-sizing]
gate: false
optional: false
---

# tam_market_sizing

## Identity

```yaml
agents:
  - name: tam_market_sizing
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Bottom-up and top-down market sizing with declared assumptions and sensitivity ranges.

## Inspiration

Derived from the Business Operations rollout planner — TAM / Market Sizing cell in the intelligence × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `statistical_analysis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Market brief.
- **Writes**: TAM/SAM/SOM memo..
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

- **System**: "You run the TAM / Market Sizing job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
