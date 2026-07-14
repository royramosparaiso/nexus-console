---
id: re_listing_completeness_monitor
name: re_listing_completeness_monitor
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: [re_transaction_doc_checklist]
produces: side_effect
tools: [document_store, read_crm]
tags: [listing, documents, completeness, real-estate]
gate: false
optional: false
---

# re_listing_completeness_monitor

## Identity

```yaml
sidecars:
  - name: re_listing_completeness_monitor
    role: worker
    mode: scheduled
    produces: side_effect
    domain: operations
    rollout_stage: 2-capture
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Listing/document completeness monitor. Checks each listing against a required-document/media checklist and flags gaps (energy certificate, floorplan, licence references) for the human to resolve.

## Trigger

Runs on a schedule (`${COMPLETENESS_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `document_store` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Listing records + attached documents/media.
- **Writes**: A per-listing completeness flag set (no legal validity assertion).
- **Depends on**: `re_transaction_doc_checklist`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
