---
id: buying_committee_mapping
name: buying_committee_mapping
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [linkedin_api, read_calls]
tags: [committee, meddpicc]
gate: false
optional: false
---

# buying_committee_mapping

## Identity

```yaml
agents:
  - name: buying_committee_mapping
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: intelligence
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

For a target account, maps the buying committee: economic buyer, champion, users, blockers — with stances and gaps.

## Inspiration

Derived from the Business Operations rollout planner — Buying-Committee Mapping cell in the intelligence × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |
| `read_calls` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account + LinkedIn + call transcripts.
- **Writes**: Committee map + gaps..
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

- **System**: "You run the Buying-Committee Mapping job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
