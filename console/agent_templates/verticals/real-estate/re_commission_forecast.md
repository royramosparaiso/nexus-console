---
id: re_commission_forecast
name: re_commission_forecast
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_crm, read_analytics]
tags: [commission, forecast, pipeline, real-estate]
gate: false
optional: false
---

# re_commission_forecast

## Identity

```yaml
sidecars:
  - name: re_commission_forecast
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Commission/pipeline forecast calculator with explicit assumptions. Projects expected commission from the weighted pipeline using configurable, stated assumptions — never a guaranteed number.

## Trigger

Runs on a schedule (`${FORECAST_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_analytics` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Pipeline stages + configurable assumption set (`${FORECAST_ASSUMPTIONS_REF}`).
- **Writes**: A forecast rollup that carries its assumptions inline.
- **Depends on**: —

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
