---
id: expansion_playbook
name: expansion_playbook
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
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_usage, read_roadmap]
tags: [expansion, upsell, csm-led]
gate: false
optional: false
---

# expansion_playbook

## Identity

```yaml
agents:
  - name: expansion_playbook
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

CSM-led. Detects expansion openings from usage + roadmap fit and drafts a proposal + plan.

## Inspiration

Derived from the Business Operations rollout planner — Renewals & Expansion cell in the customer × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_usage` | provider-specific | vendor | maybe |
| `read_roadmap` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Usage + roadmap + account.
- **Writes**: Expansion plan..
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

- **System**: "You run the Renewals & Expansion job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
