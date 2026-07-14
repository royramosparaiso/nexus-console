---
id: re_lead_enrichment
name: re_lead_enrichment
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: worker
mode: event-driven
depends_on: [re_consent_gdpr_handling]
produces: enriched_record
tools: [read_crm, enrichment_api]
tags: [lead, enrichment, consent, real-estate]
gate: false
optional: false
---

# re_lead_enrichment

## Identity

```yaml
sidecars:
  - name: re_lead_enrichment
    role: worker
    mode: event-driven
    produces: enriched_record
    domain: sales
    rollout_stage: 1-foundation
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Lead enrichment + consent-state capture. On new-lead events, enriches contactable channels and records the consent basis/source for each channel.

## Trigger

Reacts to new-lead webhooks/queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `enrichment_api` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: New lead record + consent metadata.
- **Writes**: Enriched lead with per-channel consent state + provenance.
- **Depends on**: `re_consent_gdpr_handling`

## Side effects

- Emits `enriched_record` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
