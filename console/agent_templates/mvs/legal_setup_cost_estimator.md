---
id: legal_setup_cost_estimator
name: legal_setup_cost_estimator
category: mvs
phase: 2
step: 12
role: analyst
mode: pipeline-stage
depends_on: [resource_inventory_analyst]
produces: markdown_report
tools: [web_search, fetch_url, read_intake]
tags: [legal, incorporation, trademark, tramo-0, phase-2]
gate: false
optional: false
---

# legal_setup_cost_estimator

## Identity

```yaml
- name:  legal_setup_cost_estimator
  queue: hermes-agents
  role:  analyst
  note:  Concrete cost + calendar for Tramo-0 legal setup — incorporation, trademark, domain, baseline agreements, tax registration.
```

## Purpose

Step 12. Produces a single **Capital Tramo 0 Legal** figure in the
founder's chosen currency, with low/mid/high breakdowns per line
item and actionable deadlines: company incorporation (minimum
viable form), trademark registration, primary domain, baseline
founder agreements (co-founder contract, IP assignment, NDA), and
minimum statutory tax registration. Does not cover ongoing legal
ops, GDPR compliance, client contracts or advanced IP strategy —
those belong to `legal_ip_analyst` (step 32).

## Inspiration

`legal-setup-costs` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `read_intake()` | filesystem | — | — |

## Wiring

- **Reads:** intake (jurisdiction), `11_resource_inventory.md`
- **Writes:** `12_legal_setup_costs.md`
- **Upstream:** `resource_inventory_analyst`
- **Downstream:** `tranche_0_budgeter`

## Structured output

```python
class LegalLineItem(BaseModel):
    item: str
    cost_low_eur: float
    cost_mid_eur: float
    cost_high_eur: float
    deadline_days: int
    notes: str
    sources: list[str]

class LegalSetupReport(BaseModel):
    jurisdiction: str
    line_items: list[LegalLineItem]
    total_low_eur: float
    total_mid_eur: float
    total_high_eur: float
    calendar: str                          # markdown gantt-like table
```

## Prompt shape

- **System:** "Every quoted range is anchored to a public tariff or
  recent invoice. Blank sources = drop the item. Trademark classes:
  quote per-class, not lump sum."
- **User:** jurisdiction + founder inventory.

## Extension notes

- If jurisdiction is Spain, quote the AJD, notario, registro and
  ATIB fees separately. Lumping them hides the ATIB delay risk.
