---
id: re_viewing_coordinator
name: re_viewing_coordinator
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 3
verticals: [real-estate]
role: coordinator
mode: event-driven
depends_on: [re_viewing_scheduling, re_objection_followup]
produces: markdown_report
tools: [calendar_api, email, whatsapp_api]
tags: [viewing, scheduling, follow-up, real-estate]
gate: false
optional: false
---

# re_viewing_coordinator

## Identity

```yaml
agents:
  - name: re_viewing_coordinator
    role: coordinator
    mode: event-driven
    produces: markdown_report
    domain: sales
    rollout_stage: 3-generate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Viewing coordinator. Books property viewings against agent availability, sends confirmations/reminders and drafts structured post-viewing follow-ups.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `calendar_api` | provider-specific | vendor | maybe |
| `email` | provider-specific | vendor | maybe |
| `whatsapp_api` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Buyer shortlist, agent calendars, viewing outcomes.
- **Writes**: Confirmed viewing schedule + drafted follow-up notes.
- **Upstream**: Buyer advisor and the visit-route sync sidecar.
- **Downstream**: Offer/negotiation coordinator; dormant-lead trigger if no response.
- **Depends on**: `re_viewing_scheduling`, `re_objection_followup`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_viewing_coordinator role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Confirmation SLA `${VIEWING_CONFIRM_SLA_HOURS}`. Reminders respect consent/contact-preference state.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
