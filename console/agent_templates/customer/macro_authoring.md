---
id: macro_authoring
name: macro_authoring
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [helpdesk_api, read_brand_voice]
tags: [macro, helpdesk]
gate: false
optional: false
---

# macro_authoring

## Identity

```yaml
agents:
  - name: macro_authoring
    role: writer
    mode: single-shot
    produces: structured_json
    domain: customer
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Builds and maintains helpdesk macros from repeat replies — tone-tuned to the brand.

## Inspiration

Derived from the Business Operations rollout planner — Macro Authoring cell in the customer × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `helpdesk_api` | provider-specific | vendor | maybe |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Reply corpus.
- **Writes**: Macro set..
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

- **System**: "You run the Macro Authoring job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
