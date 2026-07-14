---
id: re_crm_dedupe
name: re_crm_dedupe
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: []
produces: side_effect
tools: [read_crm, write_crm]
tags: [crm, dedupe, hygiene, real-estate]
gate: false
optional: false
---

# re_crm_dedupe

## Identity

```yaml
sidecars:
  - name: re_crm_dedupe
    role: worker
    mode: scheduled
    produces: side_effect
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
    verticals: [real-estate]
```

## Purpose

CRM dedupe/hygiene worker. Merges duplicate contacts/properties, normalizes phone/email formats and flags conflicts for human review.

## Trigger

Runs on a schedule (`${CRM_HYGIENE_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `write_crm` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: CRM contacts + property records.
- **Writes**: Merged/normalized records and a conflict-review queue.
- **Depends on**: —

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
