# Workflow — Weekly branch pipeline review & forecast

- **id**: `re_weekly_pipeline_review`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `schedule: ${WEEKLY_REVIEW_CRON}`

## Summary

Assemble the weekly branch review: run CRM hygiene to surface data-quality flags, attribute performance, compute a forecast and net-proceeds scenarios with explicit assumptions, and produce a review the branch manager signs off.

## Participating templates

- `re_crm_dedupe`
- `re_campaign_attribution`
- `re_commission_forecast`
- `re_commission_net_proceeds`
- `re_branch_pipeline_manager`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | hygiene | `re_crm_dedupe` | `crm_snapshot` | `data_quality_flags` | — |
| 2 | attribution | `re_campaign_attribution` | `campaign_touches` | `attribution_rollup` | — |
| 3 | forecast | `re_commission_forecast` | `weighted_pipeline` | `commission_forecast` | — |
| 4 | net_proceeds | `re_commission_net_proceeds` | `pipeline_scenarios` | `net_proceeds_scenarios` | — |
| 5 | review | `re_branch_pipeline_manager` | `review_inputs` | `weekly_review` | branch_manager_signs_off_review |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `branch_manager_signs_off_review` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `review_publish`: `${REVIEW_PUBLISH_SLA_HOURS}`

## Audit events

- `re_weekly_pipeline_review.hygiene.completed`
- `re_weekly_pipeline_review.attribution.completed`
- `re_weekly_pipeline_review.forecast.completed`
- `re_weekly_pipeline_review.net_proceeds.completed`
- `re_weekly_pipeline_review.review.completed`
- `re_weekly_pipeline_review.branch_manager_signs_off_review.approved`

## Success / failure outputs

- Success: `re_weekly_pipeline_review.completed`
- Failure: `re_weekly_pipeline_review.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
