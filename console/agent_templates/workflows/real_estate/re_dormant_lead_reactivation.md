# Workflow — Dormant lead → reactivation → handoff

- **id**: `re_dormant_lead_reactivation`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `schedule: ${DORMANT_SCAN_CRON}`

## Summary

Find leads idle beyond the configured age with valid consent, re-score them, draft a reactivation message, and hand them off to a human agent who accepts the handoff before any contact.

## Participating templates

- `re_dormant_lead_trigger`
- `re_consent_gdpr_handling`
- `re_lead_scoring_explainable`
- `re_objection_followup`
- `re_office_routing`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | find_dormant | `re_dormant_lead_trigger` | `lead_activity` | `dormant_candidates` | — |
| 2 | consent_check | `re_consent_gdpr_handling` | `dormant_candidates` | `eligible_leads` | — |
| 3 | rescore | `re_lead_scoring_explainable` | `eligible_leads` | `rescored_leads` | — |
| 4 | draft_reactivation | `re_objection_followup` | `rescored_leads` | `reactivation_draft` | — |
| 5 | handoff | `re_office_routing` | `rescored_leads` | `agent_assignment` | human_agent_accepts_handoff |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `human_agent_accepts_handoff` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `lead_age`: `${DORMANT_LEAD_AGE_DAYS}`

## Audit events

- `re_dormant_lead_reactivation.find_dormant.completed`
- `re_dormant_lead_reactivation.consent_check.completed`
- `re_dormant_lead_reactivation.rescore.completed`
- `re_dormant_lead_reactivation.draft_reactivation.completed`
- `re_dormant_lead_reactivation.handoff.completed`
- `re_dormant_lead_reactivation.human_agent_accepts_handoff.approved`

## Success / failure outputs

- Success: `re_dormant_lead_reactivation.completed`
- Failure: `re_dormant_lead_reactivation.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
