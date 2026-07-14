---
id: objection_library
name: objection_library
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_calls, cluster]
tags: [objections, library, enablement]
gate: false
optional: false
---

# objection_library

## Identity

```yaml
agents:
  - name: objection_library
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: deals
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Mines call transcripts to extract objections, cluster them and produce a searchable library with rebuttal drafts.

## Inspiration

Derived from the Business Operations rollout planner — Objection Library cell in the deals × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |
| `cluster` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Call transcripts.
- **Writes**: Objection clusters + rebuttal drafts..
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

- **System**: "You run the Objection Library job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
