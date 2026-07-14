---
id: deal_strategy_big_accounts
name: deal_strategy_big_accounts
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
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_notes]
tags: [strategy, big-accounts, founder-led]
gate: false
optional: false
---

# deal_strategy_big_accounts

## Identity

```yaml
agents:
  - name: deal_strategy_big_accounts
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led card. For each top-10 account, drafts a bespoke pursuit plan: stakeholders, entry point, proof, timeline, risks.

## Inspiration

Derived from the Business Operations rollout planner — Deal Strategy on Big Accounts cell in the sales × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account dossier + key contacts.
- **Writes**: Pursuit plan per account..
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

- **System**: "You run the Deal Strategy on Big Accounts job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
