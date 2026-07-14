---
id: access_collection
name: access_collection
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_stack, vault_status]
tags: [access, credentials, onboarding]
gate: false
optional: false
---

# access_collection

## Identity

```yaml
agents:
  - name: access_collection
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Drafts a per-project access-collection checklist and follow-up messages until every credential lands in the vault.

## Inspiration

Derived from the Business Operations rollout planner — Access Collection cell in the operations × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_stack` | provider-specific | vendor | maybe |
| `vault_status` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Project stack.
- **Writes**: Access checklist + reminder drafts..
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

- **System**: "You run the Access Collection job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
