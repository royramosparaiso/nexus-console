---
id: re_dormant_lead_trigger
name: re_dormant_lead_trigger
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: [re_consent_gdpr_handling]
produces: side_effect
tools: [read_crm, alerting]
tags: [dormant, reactivation, trigger, real-estate]
gate: false
optional: false
---

# re_dormant_lead_trigger

## Identity

```yaml
sidecars:
  - name: re_dormant_lead_trigger
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Dormant-lead reactivation trigger. Identifies leads idle beyond `${DORMANT_LEAD_AGE_DAYS}` with valid consent and queues them for a reactivation attempt.

## Trigger

Runs on a schedule (`${DORMANT_SCAN_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `alerting` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Lead activity history + consent state.
- **Writes**: Reactivation-eligible queue (consent-checked).
- **Depends on**: `re_consent_gdpr_handling`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
