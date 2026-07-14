---
id: strategic_account_calls
name: strategic_account_calls
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_notes]
tags: [strategic-accounts, ae-led]
gate: false
optional: false
---

# strategic_account_calls

## Identity

```yaml
agents:
  - name: strategic_account_calls
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Prepares briefing docs for named-account executive calls — history, open threads, board-level themes, questions to ask.

## Inspiration

Derived from the Business Operations rollout planner — Strategic Account Calls cell in the deals × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account dossier.
- **Writes**: Executive briefing..
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

- **System**: "You run the Strategic Account Calls job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
