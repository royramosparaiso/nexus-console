---
id: strategic_customer_accounts
name: strategic_customer_accounts
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_notes]
tags: [strategic-accounts, csm-led]
gate: false
optional: false
---

# strategic_customer_accounts

## Identity

```yaml
agents:
  - name: strategic_customer_accounts
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

CSM-led. Ongoing dossier for the top-10 customer accounts: goals, health, roadmap fit, exec relationships.

## Inspiration

Derived from the Business Operations rollout planner — Strategic Customer Accounts cell in the customer × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_notes` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Customer records.
- **Writes**: Dossier per account..
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

- **System**: "You run the Strategic Customer Accounts job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
