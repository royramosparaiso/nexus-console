---
id: pre_call_briefing
name: pre_call_briefing
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_crm, read_calendar, web_search]
tags: [briefing, prep]
gate: false
optional: false
---

# pre_call_briefing

## Identity

```yaml
agents:
  - name: pre_call_briefing
    role: writer
    mode: scheduled
    produces: markdown_report
    domain: deals
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

One hour before every call, drafts a briefing: attendee bios, company recap, last touches, likely objections, opening question.

## Inspiration

Derived from the Business Operations rollout planner — Pre-Call Briefing cell in the deals × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_calendar` | provider-specific | vendor | maybe |
| `web_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Meeting + deal + contacts.
- **Writes**: Briefing sent to AE..
- **Upstream**: signals or artefacts from foundation-stage cards in the same domain.
- **Downstream**: consumed by orchestration-stage cards or the human operator.

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the Pre-Call Briefing job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
