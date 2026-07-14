---
id: re_kyc_aml_status_monitor
name: re_kyc_aml_status_monitor
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: back-office
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: [re_kyc_aml_triage]
produces: side_effect
tools: [document_store, read_crm]
tags: [kyc, aml, compliance, monitor, real-estate]
gate: false
optional: false
---

# re_kyc_aml_status_monitor

## Identity

```yaml
sidecars:
  - name: re_kyc_aml_status_monitor
    role: worker
    mode: scheduled
    produces: side_effect
    domain: back-office
    rollout_stage: 4-orchestrate
    autonomy: human-led
    verticals: [real-estate]
```

## Purpose

KYC/AML checklist status monitor. Tracks which KYC/AML checklist items are outstanding per transaction and surfaces them for the compliance officer. **Never approves or clears** any item.

## Trigger

Runs on a schedule (`${KYC_MONITOR_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `document_store` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: KYC/AML checklist state per transaction.
- **Writes**: Outstanding-item flags routed to the human compliance queue.
- **Depends on**: `re_kyc_aml_triage`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
