---
id: cold_email_drafting
name: cold_email_drafting
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [personalization_hooks, playbook_reader]
tags: [email, cold, sequences, copy]
gate: false
optional: false
---

# cold_email_drafting

## Identity

```yaml
agents:
  - name: cold_email_drafting
    role: writer
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Drafts cold-email sequences (3-5 steps) using ICP fit, personalization brief and vertical playbook. Emits subject + body variants.

## Inspiration

Derived from the Business Operations rollout planner — Cold Email Drafting cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `personalization_hooks` | provider-specific | vendor | maybe |
| `playbook_reader` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Personalization brief + playbook.
- **Writes**: Sequence draft with A/B variants..
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

- **System**: "You run the Cold Email Drafting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
