---
id: long_form_content_writer
name: long_form_content_writer
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_brand_voice]
tags: [blog, long-form, content]
gate: false
optional: false
---

# long_form_content_writer

## Identity

```yaml
agents:
  - name: long_form_content_writer
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts full blog posts / newsletters from an SEO brief and brand voice — human edits before publish.

## Inspiration

Derived from the Business Operations rollout planner — Long-Form Content Writer cell in the marketing × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_brand_voice` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Brief + brand voice.
- **Writes**: Article draft..
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

- **System**: "You run the Long-Form Content Writer job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
