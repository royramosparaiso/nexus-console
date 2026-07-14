---
id: objection_response
name: objection_response
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [objection_library_query, read_thread]
tags: [objection, response, ae-assisted]
gate: false
optional: false
---

# objection_response

## Identity

```yaml
agents:
  - name: objection_response
    role: writer
    mode: single-shot
    produces: structured_json
    domain: deals
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

On a live thread, matches the buyer's objection to the library and drafts a response for the AE to send.

## Inspiration

Derived from the Business Operations rollout planner — Objection Response cell in the deals × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `objection_library_query` | provider-specific | vendor | maybe |
| `read_thread` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Thread + objection library.
- **Writes**: Draft response + confidence score..
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

- **System**: "You run the Objection Response job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
