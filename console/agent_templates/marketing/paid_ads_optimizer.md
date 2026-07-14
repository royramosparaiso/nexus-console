---
id: paid_ads_optimizer
name: paid_ads_optimizer
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: analyst
mode: scheduled
depends_on: []
produces: decision
tools: [meta_ads_api, google_ads_api]
tags: [paid-ads, optimization]
gate: false
optional: false
---

# paid_ads_optimizer

## Identity

```yaml
agents:
  - name: paid_ads_optimizer
    role: analyst
    mode: scheduled
    produces: decision
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: human-assisted
```

## Purpose

Watches ad performance: identifies losers, proposes bid/creative/audience mutations. Human approves before push.

## Inspiration

Derived from the Business Operations rollout planner — Paid Ads Optimizer cell in the marketing × 4-orchestrate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `meta_ads_api` | provider-specific | vendor | maybe |
| `google_ads_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Ad platform performance.
- **Writes**: Mutation proposals..
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

- **System**: "You run the Paid Ads Optimizer job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
