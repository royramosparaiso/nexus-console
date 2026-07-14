---
id: linkedin_messaging
name: linkedin_messaging
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [personalization_hooks, linkedin_style_guide]
tags: [linkedin, messaging, dm]
gate: false
optional: false
---

# linkedin_messaging

## Identity

```yaml
agents:
  - name: linkedin_messaging
    role: writer
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Drafts LinkedIn connect-notes and follow-up DMs with tone tuned to the prospect's seniority and recent activity.

## Inspiration

Derived from the Business Operations rollout planner — LinkedIn Messaging cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `personalization_hooks` | provider-specific | vendor | maybe |
| `linkedin_style_guide` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Contact + personalization brief.
- **Writes**: Multi-step DM sequence..
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

- **System**: "You run the LinkedIn Messaging job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
