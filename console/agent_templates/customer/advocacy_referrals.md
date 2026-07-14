---
id: advocacy_referrals
name: advocacy_referrals
artifact_type: agent
lifecycle: ops
category: customer
phase: null
step: null
domain: customer
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: scheduled
depends_on: []
produces: structured_json
tools: [read_nps, read_reviews]
tags: [advocacy, referral]
gate: false
optional: false
---

# advocacy_referrals

## Identity

```yaml
agents:
  - name: advocacy_referrals
    role: analyst
    mode: scheduled
    produces: structured_json
    domain: customer
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Identifies advocacy candidates (high NPS + open reviewer + case-study fit) and drafts an ask.

## Inspiration

Derived from the Business Operations rollout planner — Advocacy & Referrals cell in the customer × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_nps` | provider-specific | vendor | maybe |
| `read_reviews` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: NPS + usage + reviews.
- **Writes**: Advocacy queue + ask drafts..
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

- **System**: "You run the Advocacy & Referrals job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
