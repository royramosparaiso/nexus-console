---
id: re_referral_review_request
name: re_referral_review_request
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: customer
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm, email]
tags: [referral, review, request, skill, real-estate]
gate: false
optional: false
---

# re_referral_review_request

## Identity

```yaml
skills:
  - name: re_referral_review_request
    kind: skill
    produces: structured_json
    domain: customer
    verticals: [real-estate]
```

## Purpose

Draft referral and review-request messages personalized to a completed transaction, respecting contact/consent preferences. Drafts only.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Completed-transaction context + contact preferences.

## Outputs

Drafted referral/review messages (for human approval).

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
