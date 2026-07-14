---
id: re_matching_refresh
name: re_matching_refresh
artifact_type: sidecar
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: worker
mode: scheduled
depends_on: [re_property_matching_rank]
produces: side_effect
tools: [read_crm, search_inventory]
tags: [matching, refresh, buyers, real-estate]
gate: false
optional: false
---

# re_matching_refresh

## Identity

```yaml
sidecars:
  - name: re_matching_refresh
    role: worker
    mode: scheduled
    produces: side_effect
    domain: sales
    rollout_stage: 2-capture
    autonomy: fully-autonomous
    verticals: [real-estate]
```

## Purpose

Buyer-property matching refresh. Re-runs matching when inventory or buyer briefs change and updates each buyer's ranked candidate set.

## Trigger

Runs on a schedule and on listing-change events (`${MATCH_REFRESH_CRON}`).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `search_inventory` | provider-specific | vendor | maybe |

Credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Wiring

- **Reads**: Active buyer briefs + current inventory.
- **Writes**: Refreshed per-buyer match sets.
- **Depends on**: `re_property_matching_rank`

## Side effects

- Emits `side_effect` to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add per-provider rate-limits and back-off on 429/5xx; emit structured logs for the monitoring sidecar.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
