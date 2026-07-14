# Workflow — Cross-office workload balancing (Madrid ↔ Marbella)

- **id**: `re_cross_office_balancing`
- **version**: 0.13.5 (catalog/format version — not a release bump)
- **vertical**: real-estate
- **trigger**: `event: branch.saturation_signal / schedule: ${BALANCING_CRON}`

## Summary

Detect a saturated branch via SLA signals, propose moving overflow leads between Madrid and Marbella using pseudonymized lead IDs only, and require branch-manager approval before any reassignment.

## Participating templates

- `re_office_routing`
- `re_response_sla_monitor`
- `re_branch_pipeline_manager`

## Ordered steps

| # | Step | Template | Input state | Output state | Gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | detect_saturation | `re_response_sla_monitor` | `sla_snapshot` | `saturation_flags` | — |
| 2 | propose_rebalance | `re_office_routing` | `saturation_flags` | `rebalance_proposal` | — |
| 3 | approve_rebalance | `re_branch_pipeline_manager` | `rebalance_proposal` | `rebalance_decision` | branch_manager_approves_rebalance |

## State / payload passed

State flows step-to-step as named payload keys (see `output_state` above). PII minimization: pass only the identifiers and fields each step needs. Cross-office and aggregate steps operate on pseudonymized lead IDs and office-level rollups, never raw client contact details. Consent state is checked before any outreach.

## Human approval gates

- `branch_manager_approves_rebalance` — AI proposes; a named human must approve before the step's side effect (send / publish / reassign / clear) occurs.

## Retries & terminal states

- Retries: `${STEP_MAX_ATTEMPTS}` attempts, exponential backoff; exhausted steps route to the `human_review_queue` (dead-letter).
- Terminal states: `completed`, `failed`, `cancelled`, `expired`.

## Configurable SLAs

- `rebalance_review`: `${REBALANCE_REVIEW_SLA_HOURS}`

## Audit events

- `re_cross_office_balancing.detect_saturation.completed`
- `re_cross_office_balancing.propose_rebalance.completed`
- `re_cross_office_balancing.approve_rebalance.completed`
- `re_cross_office_balancing.branch_manager_approves_rebalance.approved`

## Success / failure outputs

- Success: `re_cross_office_balancing.completed`
- Failure: `re_cross_office_balancing.failed`

## Compliance & data notes

- KYC/AML, GDPR/consent, and property-document checks are checklists and flags with mandatory human/legal review. No approval is ever automated.
- SLAs, rates, fees and thresholds are configurable via ${VAR}; no market price, conversion rate or guarantee is invented.
- All example names, office codes and figures are illustrative and fictional.
