---
id: buyer_matching
name: buyer_matching
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: classifier
mode: scheduled
depends_on: []
produces: structured_json
tools: [read_crm, score_similarity]
tags: [matching, buyers, real-estate]
gate: false
optional: false
---

# buyer_matching

## Identity

```yaml
agents:
  - name: buyer_matching
    role: classifier
    mode: scheduled
    produces: structured_json
    domain: sales
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Matches new listings to buyer search briefs — surfaces top matches to agents.

## Inspiration

Derived from the Business Operations rollout planner — Buyer Matching cell in the sales × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `score_similarity` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Listings + buyer briefs.
- **Writes**: Match set per buyer..
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

- **System**: "You run the Buyer Matching job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
