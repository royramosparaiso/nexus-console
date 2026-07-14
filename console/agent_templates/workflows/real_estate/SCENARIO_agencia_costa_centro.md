# Reference scenario — Agencia Costa Centro (fictional)

> **Illustrative only.** *Agencia Costa Centro* is a fictional, generic example
> agency. Every name, office code, territory, capacity figure and trace below is
> made up to show how the real-estate templates and workflows compose. Nothing
> here is real market data, a real person, a real address, or any kind of
> valuation / legal / financial guarantee. All tunable numbers are shown as
> `${VAR}` placeholders that an operator sets in `nexus.secrets.env` (0600) or
> environment config — never hard-coded.

## Agency shape

Two offices, five human sales agents each (10 total). Agent codes are opaque
identifiers, not people:

| Office | Agent codes | Illustrative territory focus | Languages (illustrative) |
| --- | --- | --- | --- |
| Madrid (`MAD`) | `MAD-01`, `MAD-02`, `MAD-03`, `MAD-04`, `MAD-05` | Central-city residential zones | ES / EN |
| Marbella (`MAB`) | `MAB-01`, `MAB-02`, `MAB-03`, `MAB-04`, `MAB-05` | Coastal / second-home zones | ES / EN |

Capacity and routing metadata (illustrative, all configurable):

- Per-agent active-lead soft cap: `${AGENT_ACTIVE_LEAD_CAP}`
- Office overflow threshold: `${OFFICE_OVERFLOW_THRESHOLD}`
- First-response SLA: `${LEAD_RESPONSE_SLA_MINUTES}`
- Territory rules are declarative: a lead's location/zone maps to an owning
  office; ambiguous or cross-region leads default to `${DEFAULT_OFFICE}` and are
  flagged for a human to confirm.

### Escalation chain (illustrative)

1. Assigned human agent (e.g. `MAD-03`).
2. Office lead / duty agent for that branch.
3. Branch/pipeline manager (`re_branch_pipeline_manager`) — cross-office
   decisions, SLA breaches, rebalancing.
4. Compliance officer — any KYC/AML or GDPR item (mandatory human decision).

Routing and balancing operate on **office, territory, language and capacity**
only. They never use protected characteristics. Aggregate/cross-office steps use
pseudonymized lead IDs, not raw client contact details.

## Trace 1 — Madrid buyer (`re_buyer_lead_to_offer`)

1. `buyer_lead.created` — web enquiry (ES), interest in a central Madrid flat.
2. `re_lead_concierge` qualifies → intent=buy, language=ES, budget band=`${BAND}`.
3. `re_consent_gdpr_handling` records email+phone consent (source: web form).
4. `re_lead_scoring_explainable` → score with factors (engagement, fit, timeline).
5. `re_office_routing` + `re_territory_routing` → office `MAD`, agent `MAD-03`
   (had capacity; `MAD-01` was at soft cap).
6. `re_property_matching_rank` → 4 ranked candidates; `re_buyer_advisor`
   attaches rationale and open questions.
7. `re_viewing_coordinator` + `re_viewing_scheduling` → two viewings booked
   against `MAD-03`'s calendar within `${VIEWING_CONFIRM_SLA_HOURS}`.
8. Post-viewing, `re_objection_followup` drafts a follow-up (human sends).
9. Buyer decides to offer → `re_offer_negotiation_coordinator` prepares an offer
   decision. **Gate `human_agent_approves_offer`**: `MAD-03` approves before it
   is sent. Audit: `re_buyer_lead_to_offer.offer.completed`, then
   `...human_agent_approves_offer.approved`.

## Trace 2 — Marbella seller (`re_seller_lead_to_syndication`)

1. `seller_lead.created` — coastal villa, owner enquiry (EN).
2. `re_lead_concierge` qualifies (intent=sell); `re_office_routing` → `MAB`,
   agent `MAB-02`.
3. `re_transaction_doc_checklist` flags missing energy certificate + community
   debt certificate (flags only — legal validity confirmed by the lawyer).
4. `re_valuation_analyst` (via `re_comparables_valuation`) returns a
   **decision-support** range low/mid/high with the comps and assumptions —
   explicitly not a certified appraisal (tasación).
5. `re_listing_marketing_manager` (via `re_listing_copy_bilingual` +
   `re_portal_field_normalization`) builds the ES/EN marketing package with
   regulated fields left as flagged placeholders.
6. **Gate `human_agent_and_seller_approve_mandate_and_price`**: `MAB-02` and the
   seller approve mandate + asking price.
7. `re_portal_syndication` publishes and reconciles status back to CRM.

## Trace 3 — Cross-office overflow (`re_cross_office_balancing`)

1. `re_response_sla_monitor` detects Marbella breaching
   `${LEAD_RESPONSE_SLA_MINUTES}` on new buyer leads (all five `MAB` agents at
   soft cap) → `saturation_flags`.
2. `re_office_routing` proposes moving `${OVERFLOW_BATCH_SIZE}` pseudonymized
   overflow leads to Madrid agents with spare capacity (`MAD-04`, `MAD-05`).
   Proposal carries lead IDs only — no client PII.
3. **Gate `branch_manager_approves_rebalance`**: `re_branch_pipeline_manager`
   reviews and approves. Only then are leads reassigned. Audit:
   `re_cross_office_balancing.approve_rebalance.completed` +
   `...branch_manager_approves_rebalance.approved`.

## How this maps to the catalogue

- **Agents** own accountable roles (concierge, advisor, coordinators, branch
  manager). **Sidecars** do the deterministic, event/scheduled plumbing (routing,
  SLA, syndication, monitors, forecasts). **Skills** are the reusable capabilities
  the agents and sidecars call (qualification, consent, scoring, matching,
  valuation, checklists, drafting). Composition is preferred over super-agents.
- Every workflow that takes an outward action (send, publish, reassign, clear a
  compliance item, complete at notary) passes through an explicit human approval
  gate. KYC/AML, GDPR/consent and property-document checks are always
  human/legal decisions.
