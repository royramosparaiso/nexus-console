---
id: pricing_research
name: pricing_research
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [web_search, fetch_url]
tags: [pricing, competitive]
gate: false
optional: false
---

# pricing_research

## Identity

```yaml
agents:
  - name: pricing_research
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Reconstructs a competitor's pricing from public pages + procurement leaks + community reports.

## Inspiration

Derived from the Business Operations rollout planner — Pricing Research cell in the intelligence × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `fetch_url` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Competitor list.
- **Writes**: Pricing teardown..
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

- **System**: "You run the Pricing Research job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
