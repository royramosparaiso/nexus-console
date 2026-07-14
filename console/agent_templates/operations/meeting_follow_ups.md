---
id: meeting_follow_ups
name: meeting_follow_ups
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: event-driven
depends_on: []
produces: structured_json
tools: [read_calls, read_calendar]
tags: [follow-up, meetings]
gate: false
optional: false
---

# meeting_follow_ups

## Identity

```yaml
agents:
  - name: meeting_follow_ups
    role: writer
    mode: event-driven
    produces: structured_json
    domain: operations
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

After every meeting, drafts recap + action items + follow-up email — one bundle per attendee group.

## Inspiration

Derived from the Business Operations rollout planner — Meeting Follow-Ups cell in the operations × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_calls` | provider-specific | vendor | maybe |
| `read_calendar` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Meeting transcript + calendar.
- **Writes**: Follow-up bundle..
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

- **System**: "You run the Meeting Follow-Ups job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
