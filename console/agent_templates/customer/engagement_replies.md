---
id: engagement_replies
name: engagement_replies
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
produces: structured_json
tools: [helpdesk_api, docs_search, read_brand_voice]
tags: [reply, helpdesk]
gate: false
optional: false
---

# engagement_replies

## Identity

```yaml
agents:
  - name: engagement_replies
    role: writer
    mode: event-driven
    produces: structured_json
    domain: customer
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Drafts personal replies to tickets — brand-voice tuned, cited from docs, human clicks send.

## Inspiration

Derived from the Business Operations rollout planner — Engagement & Replies cell in the customer × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `helpdesk_api` | provider-specific | vendor | maybe |
| `docs_search` | provider-specific | vendor | maybe |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ticket thread + docs.
- **Writes**: Reply draft..
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

- **System**: "You run the Engagement & Replies job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
