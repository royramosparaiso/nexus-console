---
id: referral_capture
name: referral_capture
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: classifier
mode: event-driven
depends_on: []
produces: structured_json
tools: [read_thread, crm_upsert]
tags: [referral, capture]
gate: false
optional: false
---

# referral_capture

## Identity

```yaml
agents:
  - name: referral_capture
    role: classifier
    mode: event-driven
    produces: structured_json
    domain: deals
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Detects referral offers in replies, extracts referred contact, opens a new record and drafts an intro email.

## Inspiration

Derived from the Business Operations rollout planner — Referral Capture cell in the deals × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_thread` | provider-specific | vendor | maybe |
| `crm_upsert` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Reply thread.
- **Writes**: Referred contact + intro draft..
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

- **System**: "You run the Referral Capture job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
