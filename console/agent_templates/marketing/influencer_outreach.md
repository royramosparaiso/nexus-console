---
id: influencer_outreach
name: influencer_outreach
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [social_search, engagement_analysis]
tags: [influencer, outreach, creator]
gate: false
optional: false
---

# influencer_outreach

## Identity

```yaml
agents:
  - name: influencer_outreach
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 2-capture
    autonomy: human-assisted
```

## Purpose

Finds influencers matching the brand, scores fit, drafts outreach — human approves the shortlist and copy.

## Inspiration

Derived from the Business Operations rollout planner — Influencer Outreach cell in the marketing × 2-capture × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `social_search` | provider-specific | vendor | maybe |
| `engagement_analysis` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: ICP + brand voice.
- **Writes**: Ranked influencer list + drafts..
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

- **System**: "You run the Influencer Outreach job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
