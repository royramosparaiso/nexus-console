---
id: re_lead_qualification_bilingual
name: re_lead_qualification_bilingual
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [language_detect, llm]
tags: [lead, qualification, bilingual, skill, real-estate]
gate: false
optional: false
---

# re_lead_qualification_bilingual

## Identity

```yaml
skills:
  - name: re_lead_qualification_bilingual
    kind: skill
    produces: structured_json
    domain: sales
    verticals: [real-estate]
```

## Purpose

Qualify a real-estate lead in Spanish or English: detect language, extract intent (buy/sell/rent), budget band, timeline and location interest into a structured record.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `language_detect` | provider-specific | vendor | maybe |
| `llm` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Raw enquiry text (ES/EN) + any known contact fields.

## Outputs

Structured qualification record (intent, language, criteria, missing fields).

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: —

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
