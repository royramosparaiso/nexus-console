---
id: re_portal_syndication
name: re_portal_syndication
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: connector
mode: scheduled
depends_on: [re_portal_field_normalization]
produces: side_effect
tools: [portal_api, read_crm]
tags: [portal, syndication, reconciliation, real-estate]
gate: false
optional: false
---

# re_portal_syndication

## Identity

```yaml
sidecars:
  - name: re_portal_syndication
    role: connector
    mode: scheduled
    produces: side_effect
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Portal syndication + listing-status reconciliation. Publishes approved listings to portals and reconciles status (active/reserved/sold) back into the CRM.

## Trigger

Runs on a schedule (`${PORTAL_SYNC_CRON}`); publish only after human approval.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `portal_api` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Approved listings + portal responses.
- **Writes**: Portal publications + reconciled listing-status updates.
- **Depends on**: `re_portal_field_normalization`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
