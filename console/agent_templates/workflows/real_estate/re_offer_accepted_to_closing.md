# Workflow — Offer accepted → closing → after-sales

- **id**: `re_offer_accepted_to_closing`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `event: offer.accepted`

## Summary

From an accepted offer to completion and after-sales: triage KYC/AML (human compliance sign-off required — never automated), coordinate the transaction, monitor deadlines, complete at notary (human), then run after-sales and referral asks.

## Participating templates

- `re_offer_negotiation_coordinator`
- `re_kyc_aml_triage`
- `re_kyc_aml_status_monitor`
- `re_transaction_coordinator`
- `re_transaction_doc_checklist`
- `re_offer_deadline_monitor`
- `closing_coordination`
- `re_aftersales_referral_agent`
- `re_referral_review_request`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | kyc_triage | `re_kyc_aml_triage` | `accepted_offer` | `kyc_status` | — |
| 2 | kyc_signoff | `re_kyc_aml_status_monitor` | `kyc_status` | `kyc_cleared_flag` | compliance_officer_clears_kyc_aml |
| 3 | coordinate | `re_transaction_coordinator` | `accepted_offer` | `transaction_plan` | — |
| 4 | track_deadlines | `re_offer_deadline_monitor` | `transaction_plan` | `deadline_alerts` | — |
| 5 | close | `closing_coordination` | `transaction_plan` | `closing_summary` | human_completes_notary_and_completion |
| 6 | after_sales | `re_aftersales_referral_agent` | `closing_summary` | `aftersales_plan` | — |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `compliance_officer_clears_kyc_aml` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.
- `human_completes_notary_and_completion` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `kyc_review`: `${KYC_REVIEW_SLA_HOURS}`
- `deadline_buffer`: `${DEADLINE_BUFFER_HOURS}`

## Audit events

- `re_offer_accepted_to_closing.kyc_triage.completed`
- `re_offer_accepted_to_closing.kyc_signoff.completed`
- `re_offer_accepted_to_closing.coordinate.completed`
- `re_offer_accepted_to_closing.track_deadlines.completed`
- `re_offer_accepted_to_closing.close.completed`
- `re_offer_accepted_to_closing.after_sales.completed`
- `re_offer_accepted_to_closing.compliance_officer_clears_kyc_aml.approved`
- `re_offer_accepted_to_closing.human_completes_notary_and_completion.approved`

## Success / failure outputs

- Success: `re_offer_accepted_to_closing.completed`
- Failure: `re_offer_accepted_to_closing.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
