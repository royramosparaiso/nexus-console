---
id: creative_asset_repurpose
name: creative_asset_repurpose
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_brand_voice]
tags: [repurpose, content, atomization]
gate: false
optional: false
---

# creative_asset_repurpose

## Identity

```yaml
agents:
  - name: creative_asset_repurpose
    role: writer
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

From one hero asset (long-form video, blog, whitepaper), fans out 10-30 micro-assets across channels.

## Inspiration

Derived from the Business Operations rollout planner — Creative Asset Repurpose cell in the marketing × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Source asset.
- **Writes**: Micro-assets bundle..
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

- **System**: "You run the Creative Asset Repurpose job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
