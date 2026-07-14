---
id: social_posts_generator
name: social_posts_generator
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_brand_voice]
tags: [social, posts, repurpose]
gate: false
optional: false
---

# social_posts_generator

## Identity

```yaml
agents:
  - name: social_posts_generator
    role: writer
    mode: single-shot
    produces: structured_json
    domain: marketing
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

From a source (post, video, event) drafts platform-specific posts for LinkedIn, X, Instagram, TikTok with hooks and hashtags.

## Inspiration

Derived from the Business Operations rollout planner — Social Posts Generator cell in the marketing × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Source content + brand voice.
- **Writes**: Platform posts..
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

- **System**: "You run the Social Posts Generator job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
