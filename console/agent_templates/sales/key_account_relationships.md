---
id: key_account_relationships
name: key_account_relationships
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_notes]
tags: [strategic-accounts, relationships, founder-led]
gate: false
optional: false
---

# key_account_relationships

## Identity

```yaml
agents:
  - name: key_account_relationships
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led card. Tracks the top strategic accounts, mapped stakeholders, current stage, next best action.

## Inspiration

Derived from the Business Operations rollout planner — Key-Account Relationships cell in the sales × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: CRM strategic tier.
- **Writes**: Relationship dossier per account..
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

- **System**: "You run the Key-Account Relationships job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
