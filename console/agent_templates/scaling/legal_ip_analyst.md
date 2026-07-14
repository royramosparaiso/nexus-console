---
id: legal_ip_analyst
name: legal_ip_analyst
artifact_type: agent
lifecycle: project
category: scaling
phase: 4
step: 32
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: analyst
mode: pipeline-stage
depends_on: [legal_setup_cost_estimator, data_schema_designer, tech_stack_vendors_analyst]
produces: markdown_report
tools: [web_search, fetch_url, read_prior_step]
tags: [legal, gdpr, dpa, terms, ip, trademark, phase-4]
gate: false
optional: false
---

# legal_ip_analyst

## Identity

```yaml
- name:  legal_ip_analyst
  queue: hermes-agents
  role:  analyst
  note:  Full legal and IP posture for scale — DPA, GDPR RoPA, terms/privacy/cookies, IP protection, sub-processor register.
```

## Purpose

Step 32. Extends step 12 with the scale-stage legal posture: full
DPA with clients, GDPR Record of Processing Activities, terms of
service, privacy policy and cookie banner, sub-processor register
tied to step 31, trademark strategy (extra classes, geographies),
patents / trade secrets, open-source license posture, contract
templates for sales.

## Inspiration

`legal-ip-analysis` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 12, 28, 31
- **Writes:** `32_legal_ip.md`
- **Upstream:** `legal_setup_cost_estimator`, `data_schema_designer`, `tech_stack_vendors_analyst`
- **Downstream:** `risk_assessor`, `financial_business_planner`

## Structured output

```python
class LegalDeliverable(BaseModel):
    deliverable: str
    status: Literal["required", "recommended"]
    cost_eur: float
    deadline_days: int
    responsible: str

class LegalIpReport(BaseModel):
    deliverables: list[LegalDeliverable]
    subprocessor_register: list[str]
    trademark_extensions: list[str]
    ip_protection_strategy: str
    open_source_posture: str
```

## Prompt shape

- **System:** "GDPR compliance is not one document — it is a
  posture. RoPA + DPA + sub-processors must all appear or the
  posture is broken."
- **User:** step 28 PII fields + step 31 vendors + step 12 baseline.

## Extension notes

- Sub-processor register must match the step 31 vendor list
  exactly.
