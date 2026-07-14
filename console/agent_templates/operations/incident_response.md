---
id: incident_response
name: incident_response
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: coordinator
mode: event-driven
depends_on: []
produces: markdown_report
tools: [war_room, post_slack, read_metrics]
tags: [incident, postmortem]
gate: false
optional: false
---

# incident_response

## Identity

```yaml
agents:
  - name: incident_response
    role: coordinator
    mode: event-driven
    produces: markdown_report
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Coordinates incident playbook: opens war-room, drafts status updates, tracks timeline, writes postmortem.

## Inspiration

Derived from the Business Operations rollout planner — Incident Response cell in the operations × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `war_room` | provider-specific | vendor | maybe |
| `post_slack` | provider-specific | vendor | maybe |
| `read_metrics` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Alert + timeline.
- **Writes**: Incident report + postmortem..
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

- **System**: "You run the Incident Response job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
