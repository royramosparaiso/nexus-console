---
id: re_aftersales_referral_agent
name: re_aftersales_referral_agent
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: writer
mode: single-shot
depends_on: [re_referral_review_request]
produces: structured_json
tools: [read_crm, email]
tags: [after-sales, referral, review, real-estate]
gate: false
optional: false
---

# re_aftersales_referral_agent

## Identity

```yaml
agents:
  - name: re_aftersales_referral_agent
    role: writer
    mode: single-shot
    produces: structured_json
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

After-sales/referral agent. After completion, drafts a follow-up plan, review requests and referral asks, and schedules periodic check-ins to keep the relationship warm.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Completed-transaction record + client contact preferences.
- **Writes**: A drafted after-sales sequence (review + referral asks) for human approval.
- **Upstream**: Transaction coordinator on completion.
- **Downstream**: CRM (nurture) and the dormant-lead reactivation flow.
- **Depends on**: `re_referral_review_request`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_aftersales_referral_agent role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Only contacts clients with valid consent. All outreach is drafted for human approval before sending.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
