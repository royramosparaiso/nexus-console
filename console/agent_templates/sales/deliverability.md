---
id: deliverability
name: deliverability
artifact_type: sidecar
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [dns_check, blocklist_check, warmup]
tags: [deliverability, email, spf, dkim, dmarc]
gate: false
optional: false
---

# deliverability

## Identity

```yaml
sidecars:
  - name: deliverability
    role: worker
    mode: scheduled
    produces: side_effect
    domain: sales
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Monitors SPF/DKIM/DMARC, warms up inboxes, watches blocklists, alerts on bounce-rate spikes.

## Trigger

Sidecar runs on a fixed cron cadence.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `dns_check` | provider-specific | vendor | maybe |
| `blocklist_check` | provider-specific | vendor | maybe |
| `warmup` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Inbox list + DNS records.
- **Writes**: Deliverability status per inbox + alerts..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
