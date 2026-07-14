---
id: warm_intro_pathing
name: warm_intro_pathing
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [linkedin_api, address_book]
tags: [warm-intro, network]
gate: false
optional: false
---

# warm_intro_pathing

## Identity

```yaml
agents:
  - name: warm_intro_pathing
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 2-capture
    autonomy: human-led
```

## Purpose

Analyst-led. From LinkedIn graph and address book, drafts the best warm-intro path to a target contact.

## Inspiration

Derived from the Business Operations rollout planner — Warm Intro cell in the intelligence × 2-capture × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |
| `address_book` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Address book + LinkedIn.
- **Writes**: Intro path + ask draft..
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

- **System**: "You run the Warm Intro job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
