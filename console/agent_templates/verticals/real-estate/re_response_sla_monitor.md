---
id: re_response_sla_monitor
name: re_response_sla_monitor
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 3
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_crm, alerting]
tags: [sla, response, escalation, real-estate]
gate: false
optional: false
---

# re_response_sla_monitor

## Identity

```yaml
sidecars:
  - name: re_response_sla_monitor
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Response SLA monitor/escalation. Watches first-response time against `${LEAD_RESPONSE_SLA_MINUTES}` and escalates breaches to the branch manager.

## Trigger

Runs on a short schedule (`${SLA_MONITOR_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `alerting` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Lead timestamps + assignment state.
- **Writes**: Escalation events for at-risk/breached leads.
- **Depends on**: —

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
