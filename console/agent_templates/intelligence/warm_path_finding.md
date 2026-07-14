---
id: warm_path_finding
name: warm_path_finding
artifact_type: sidecar
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: structured_json
tools: [linkedin_api]
tags: [warm-path, network]
gate: false
optional: false
---

# warm_path_finding

## Identity

```yaml
sidecars:
  - name: warm_path_finding
    role: worker
    mode: event-driven
    produces: structured_json
    domain: intelligence
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Continuously scans your network for warm paths into target accounts as new connections and job changes appear.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Target list + LinkedIn graph.
- **Writes**: Warm-path suggestions..

## Side effects

- Emits structured_json to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
