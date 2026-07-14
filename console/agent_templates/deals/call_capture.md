---
id: call_capture
name: call_capture
artifact_type: sidecar
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [gong_api, fireflies_api, otter_api]
tags: [call, transcription, summary]
gate: false
optional: false
---

# call_capture

## Identity

```yaml
sidecars:
  - name: call_capture
    role: worker
    mode: event-driven
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Records, transcribes and diarises sales calls; pushes structured summaries back to the CRM against the right deal.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `gong_api` | provider-specific | vendor | maybe |
| `fireflies_api` | provider-specific | vendor | maybe |
| `otter_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Meeting bot output.
- **Writes**: Transcript + summary attached to deal..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
