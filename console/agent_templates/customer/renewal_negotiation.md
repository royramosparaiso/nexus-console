---
id: renewal_negotiation
name: renewal_negotiation
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
tools: [read_crm, read_usage]
tags: [renewal, csm-led]
gate: false
optional: false
---

# renewal_negotiation

## Identity

```yaml
agents:
  - name: renewal_negotiation
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

CSM-led. Drafts renewal position and negotiation brief for the CSM to run the conversation.

## Inspiration

Derived from the Business Operations rollout planner — Renewal Negotiation cell in the customer × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_usage` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account health + usage.
- **Writes**: Renewal brief..
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

- **System**: "You run the Renewal Negotiation job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
