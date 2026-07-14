---
id: faq_self_serve
name: faq_self_serve
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
mode: event-driven
depends_on: []
produces: markdown_report
tools: [helpdesk_api, docs_search]
tags: [kb, self-serve]
gate: false
optional: false
---

# faq_self_serve

## Identity

```yaml
agents:
  - name: faq_self_serve
    role: writer
    mode: event-driven
    produces: markdown_report
    domain: customer
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

From tickets and docs, auto-drafts FAQ entries and self-serve articles for repeat questions.

## Inspiration

Derived from the Business Operations rollout planner — FAQ & Self-Serve cell in the customer × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `helpdesk_api` | provider-specific | vendor | maybe |
| `docs_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ticket corpus + docs.
- **Writes**: Draft KB article..
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

- **System**: "You run the FAQ & Self-Serve job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
