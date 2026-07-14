---
id: video_prospecting
name: video_prospecting
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 1
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [personalization_hooks]
tags: [video, prospecting, loom]
gate: false
optional: false
---

# video_prospecting

## Identity

```yaml
agents:
  - name: video_prospecting
    role: writer
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Generates a per-prospect video script and thumbnail brief for tools like Loom/Sendspark — persona-tuned, 45-60 seconds.

## Inspiration

Derived from the Business Operations rollout planner — Video Prospecting cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `personalization_hooks` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Personalization brief.
- **Writes**: Video script + thumbnail brief + suggested CTA..
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

- **System**: "You run the Video Prospecting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
