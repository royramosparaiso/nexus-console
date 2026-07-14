# Workflow — Buyer lead → offer

- **id**: `re_buyer_lead_to_offer`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `event: buyer_lead.created`

## Summary

From a new buyer enquiry to a human-approved offer: qualify, consent-check, score, route to office/agent, match inventory, advise, schedule viewings, follow up, and prepare an offer that a human agent must approve before it is sent.

## Participating templates

- `re_lead_concierge`
- `re_lead_qualification_bilingual`
- `re_consent_gdpr_handling`
- `re_lead_scoring_explainable`
- `re_office_routing`
- `re_territory_routing`
- `re_buyer_advisor`
- `re_requirements_normalization`
- `re_property_matching_rank`
- `re_viewing_coordinator`
- `re_viewing_scheduling`
- `re_objection_followup`
- `re_offer_negotiation_coordinator`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | qualify | `re_lead_concierge` | `raw_enquiry` | `qualified_lead` | — |
| 2 | consent_check | `re_consent_gdpr_handling` | `qualified_lead` | `consent_state` | — |
| 3 | score | `re_lead_scoring_explainable` | `qualified_lead` | `scored_lead` | — |
| 4 | route | `re_office_routing` | `scored_lead` | `assignment` | — |
| 5 | match | `re_property_matching_rank` | `buyer_brief` | `ranked_matches` | — |
| 6 | advise | `re_buyer_advisor` | `ranked_matches` | `shortlist` | — |
| 7 | schedule_viewing | `re_viewing_coordinator` | `shortlist` | `viewing_schedule` | — |
| 8 | follow_up | `re_objection_followup` | `viewing_outcome` | `follow_up_draft` | — |
| 9 | offer | `re_offer_negotiation_coordinator` | `buyer_intent` | `offer_decision` | human_agent_approves_offer |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `human_agent_approves_offer` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `first_response`: `${LEAD_RESPONSE_SLA_MINUTES}`
- `viewing_confirm`: `${VIEWING_CONFIRM_SLA_HOURS}`

## Audit events

- `re_buyer_lead_to_offer.qualify.completed`
- `re_buyer_lead_to_offer.consent_check.completed`
- `re_buyer_lead_to_offer.score.completed`
- `re_buyer_lead_to_offer.route.completed`
- `re_buyer_lead_to_offer.match.completed`
- `re_buyer_lead_to_offer.advise.completed`
- `re_buyer_lead_to_offer.schedule_viewing.completed`
- `re_buyer_lead_to_offer.follow_up.completed`
- `re_buyer_lead_to_offer.offer.completed`
- `re_buyer_lead_to_offer.human_agent_approves_offer.approved`

## Success / failure outputs

- Success: `re_buyer_lead_to_offer.completed`
- Failure: `re_buyer_lead_to_offer.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
