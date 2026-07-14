---
id: re_objection_followup
name: re_objection_followup
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm]
tags: [objection, follow-up, drafting, skill, real-estate]
gate: false
optional: false
---

# re_objection_followup

## Identity

```yaml
skills:
  - name: re_objection_followup
    kind: skill
    produces: structured_json
    domain: deals
    verticals: [real-estate]
```

## Purpose

Draft objection-handling responses and a follow-up sequence tailored to the interaction context, for human review before sending.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Interaction context + detected objections.

## Outputs

Drafted responses + a follow-up sequence (draft).

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
