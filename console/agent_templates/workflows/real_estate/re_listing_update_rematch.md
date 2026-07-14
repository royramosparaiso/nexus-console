# Workflow — New/updated listing → buyer rematch

- **id**: `re_listing_update_rematch`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `event: listing.created_or_updated / market_listing.changed`

## Summary

When inventory or the market changes, refresh buyer matches and drive prioritized outreach — but only to buyers whose consent state permits it, and only after a human approves the outreach list.

## Participating templates

- `re_market_listing_watcher`
- `re_matching_refresh`
- `re_property_matching_rank`
- `re_consent_gdpr_handling`
- `re_buyer_advisor`
- `re_objection_followup`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | detect_change | `re_market_listing_watcher` | `market_signal` | `change_event` | — |
| 2 | refresh_matches | `re_matching_refresh` | `change_event` | `updated_match_sets` | — |
| 3 | rank | `re_property_matching_rank` | `buyer_brief` | `ranked_matches` | — |
| 4 | consent_check | `re_consent_gdpr_handling` | `buyer_contact` | `consent_state` | — |
| 5 | prioritized_outreach | `re_buyer_advisor` | `ranked_matches` | `outreach_shortlist` | human_agent_approves_outreach |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `human_agent_approves_outreach` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `outreach_window`: `${REMATCH_OUTREACH_SLA_HOURS}`

## Audit events

- `re_listing_update_rematch.detect_change.completed`
- `re_listing_update_rematch.refresh_matches.completed`
- `re_listing_update_rematch.rank.completed`
- `re_listing_update_rematch.consent_check.completed`
- `re_listing_update_rematch.prioritized_outreach.completed`
- `re_listing_update_rematch.human_agent_approves_outreach.approved`

## Success / failure outputs

- Success: `re_listing_update_rematch.completed`
- Failure: `re_listing_update_rematch.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
