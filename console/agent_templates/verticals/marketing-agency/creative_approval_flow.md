---
id: creative_approval_flow
name: creative_approval_flow
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [marketing-agency]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [notion_api, email]
tags: [approval, creative, agency]
gate: false
optional: false
---

# creative_approval_flow

## Identity

```yaml
sidecars:
  - name: creative_approval_flow
    role: connector
    mode: event-driven
    produces: side_effect
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Runs creative through client-approval steps with reminders, version tracking, redlines.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `notion_api` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Creative asset + client SLA.
- **Writes**: Approval state..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
