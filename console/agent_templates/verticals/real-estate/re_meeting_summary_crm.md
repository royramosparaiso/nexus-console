---
id: re_meeting_summary_crm
name: re_meeting_summary_crm
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [llm, write_crm]
tags: [summary, crm, notes, skill, real-estate]
gate: false
optional: false
---

# re_meeting_summary_crm

## Identity

```yaml
skills:
  - name: re_meeting_summary_crm
    kind: skill
    produces: structured_json
    domain: deals
    verticals: [real-estate]
```

## Purpose

Summarize a call/viewing/meeting and structure it into CRM notes (outcome, next step, objections, follow-up date).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `llm` | provider-specific | vendor | maybe |
| `write_crm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Transcript or notes from an interaction.

## Outputs

Structured CRM note + suggested next action.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
