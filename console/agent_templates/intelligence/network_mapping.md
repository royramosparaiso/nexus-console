---
id: network_mapping
name: network_mapping
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
produces: structured_json
tools: [linkedin_api, web_search]
tags: [network, graph, stakeholders]
gate: false
optional: false
---

# network_mapping

## Identity

```yaml
agents:
  - name: network_mapping
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: intelligence
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Analyst-led. Maps stakeholder networks around a target account or ecosystem: nodes, edges, influence flow.

## Inspiration

Derived from the Business Operations rollout planner — Network Mapping cell in the intelligence × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |
| `web_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: LinkedIn + press + CRM.
- **Writes**: Network graph..
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

- **System**: "You run the Network Mapping job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
