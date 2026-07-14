---
id: market_mapping
name: market_mapping
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [web_search, wide_browse, fetch_url]
tags: [market-map, landscape, accounts]
gate: false
optional: false
---

# market_mapping

## Identity

```yaml
agents:
  - name: market_mapping
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Builds a landscape map of every company matching the ICP in a target geography — segmented by size, sector, funding, tech stack.

## Inspiration

Derived from the Business Operations rollout planner — Market Mapping cell in the sales × 1-foundation × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `wide_browse` | provider-specific | vendor | maybe |
| `fetch_url` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: ICP + geo scope.
- **Writes**: Structured account list..
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

- **System**: "You run the Market Mapping job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
