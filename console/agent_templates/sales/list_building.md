---
id: list_building
name: list_building
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: integrator
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_crm, score_accounts]
tags: [list, prioritization, outreach]
gate: false
optional: false
---

# list_building

## Identity

```yaml
agents:
  - name: list_building
    role: integrator
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Consolidates raw accounts from mining + scraping + social into ranked outreach lists per persona and channel.

## Inspiration

Derived from the Business Operations rollout planner — List Building cell in the sales × 1-foundation × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `score_accounts` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Staged accounts + ICP + persona map.
- **Writes**: Ranked list per campaign..
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

- **System**: "You run the List Building job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
