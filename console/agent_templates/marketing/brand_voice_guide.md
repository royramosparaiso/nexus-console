---
id: brand_voice_guide
name: brand_voice_guide
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 1-foundation
autonomy: human-led
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_content, read_interviews]
tags: [brand-voice, founder-led]
gate: false
optional: false
---

# brand_voice_guide

## Identity

```yaml
agents:
  - name: brand_voice_guide
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 1-foundation
    autonomy: human-led
```

## Purpose

Founder-led. Codifies tone, do's/don'ts, vocabulary, examples — the source of truth every content agent reads.

## Inspiration

Derived from the Business Operations rollout planner — Brand Voice Guide cell in the marketing × 1-foundation × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_content` | provider-specific | vendor | maybe |
| `read_interviews` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Existing content + interviews.
- **Writes**: Brand voice guide markdown..
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

- **System**: "You run the Brand Voice Guide job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
