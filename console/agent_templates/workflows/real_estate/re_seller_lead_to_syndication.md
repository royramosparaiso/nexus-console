# Workflow — Seller lead → listing syndication

- **id**: `re_seller_lead_to_syndication`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `event: seller_lead.created`

## Summary

From a seller enquiry to a syndicated listing: qualify, route, build the acquisition brief, run the document checklist, produce valuation support and marketing content, obtain explicit human + seller approval of mandate and price, then syndicate to portals.

## Participating templates

- `re_lead_concierge`
- `re_office_routing`
- `re_listing_acquisition_manager`
- `re_transaction_doc_checklist`
- `re_listing_completeness_monitor`
- `re_valuation_analyst`
- `re_comparables_valuation`
- `re_listing_marketing_manager`
- `re_listing_copy_bilingual`
- `re_portal_field_normalization`
- `re_portal_syndication`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | qualify | `re_lead_concierge` | `raw_enquiry` | `qualified_seller_lead` | — |
| 2 | route | `re_office_routing` | `qualified_seller_lead` | `assignment` | — |
| 3 | acquire | `re_listing_acquisition_manager` | `seller_context` | `acquisition_brief` | — |
| 4 | doc_checklist | `re_transaction_doc_checklist` | `property_facts` | `doc_status` | — |
| 5 | valuation_support | `re_valuation_analyst` | `property_facts` | `valuation_range` | — |
| 6 | marketing_pack | `re_listing_marketing_manager` | `approved_listing` | `marketing_package` | — |
| 7 | mandate_approval | `re_listing_acquisition_manager` | `acquisition_brief` | `signed_mandate` | human_agent_and_seller_approve_mandate_and_price |
| 8 | syndicate | `re_portal_syndication` | `marketing_package` | `portal_publications` | — |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `human_agent_and_seller_approve_mandate_and_price` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `first_response`: `${LEAD_RESPONSE_SLA_MINUTES}`

## Audit events

- `re_seller_lead_to_syndication.qualify.completed`
- `re_seller_lead_to_syndication.route.completed`
- `re_seller_lead_to_syndication.acquire.completed`
- `re_seller_lead_to_syndication.doc_checklist.completed`
- `re_seller_lead_to_syndication.valuation_support.completed`
- `re_seller_lead_to_syndication.marketing_pack.completed`
- `re_seller_lead_to_syndication.mandate_approval.completed`
- `re_seller_lead_to_syndication.syndicate.completed`
- `re_seller_lead_to_syndication.human_agent_and_seller_approve_mandate_and_price.approved`

## Success / failure outputs

- Success: `re_seller_lead_to_syndication.completed`
- Failure: `re_seller_lead_to_syndication.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
