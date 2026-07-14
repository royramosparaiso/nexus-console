---
id: campaign_launch
name: campaign_launch
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [outreach_api, instantly_api, apollo_api]
tags: [campaign, launch, outbound]
gate: false
optional: false
---

# campaign_launch

## Identity

```yaml
sidecars:
  - name: campaign_launch
    role: connector
    mode: event-driven
    produces: side_effect
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Pushes approved sequences into the outbound tool (Outreach, Instantly, Apollo) with the right list, cadence and A/B split.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `outreach_api` | provider-specific | vendor | maybe |
| `instantly_api` | provider-specific | vendor | maybe |
| `apollo_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Approved sequence draft + list.
- **Writes**: Campaign created on outbound platform..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
