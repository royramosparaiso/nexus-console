---
id: follow_up_drafting
name: follow_up_drafting
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: structured_json
tools: [read_calls, read_crm]
tags: [follow-up, email]
gate: false
optional: false
---

# follow_up_drafting

## Identity

```yaml
agents:
  - name: follow_up_drafting
    role: writer
    mode: event-driven
    produces: structured_json
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

After every meeting, drafts a follow-up email with the recap, agreed next steps and any attachments — ready to send.

## Inspiration

Derived from the Business Operations rollout planner — Follow-Up Drafting cell in the deals × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Call debrief + deal.
- **Writes**: Follow-up email draft..
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

- **System**: "You run the Follow-Up Drafting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
