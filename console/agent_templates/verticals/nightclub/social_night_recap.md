---
id: social_night_recap
name: social_night_recap
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [nightclub]
role: writer
mode: event-driven
depends_on: []
produces: structured_json
tools: [instagram_api, read_media]
tags: [social, recap, nightclub]
gate: false
optional: false
---

# social_night_recap

## Identity

```yaml
agents:
  - name: social_night_recap
    role: writer
    mode: event-driven
    produces: structured_json
    domain: operations
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Assembles next-morning night recap posts: highlights, DJ tags, upcoming week — for Instagram + TikTok.

## Inspiration

Derived from the Business Operations rollout planner — Social Night Recap cell in the operations × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `instagram_api` | provider-specific | vendor | maybe |
| `read_media` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Night KPIs + media.
- **Writes**: Recap posts..
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

- **System**: "You run the Social Night Recap job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
