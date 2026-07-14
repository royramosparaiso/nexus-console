---
id: transcript_processing
name: transcript_processing
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [fireflies_api, notion_api]
tags: [transcript, meetings]
gate: false
optional: false
---

# transcript_processing

## Identity

```yaml
sidecars:
  - name: transcript_processing
    role: worker
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Watches meeting-recorder outputs, cleans transcripts, extracts action items, publishes to the right channel.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fireflies_api` | provider-specific | vendor | maybe |
| `notion_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Meeting recorder stream.
- **Writes**: Cleaned transcript + action items..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
