---
id: seo_briefs
name: seo_briefs
artifact_type: agent
lifecycle: ops
category: marketing
phase: null
step: null
domain: marketing
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [serp_api, keyword_tools, web_search]
tags: [seo, brief, content]
gate: false
optional: false
---

# seo_briefs

## Identity

```yaml
agents:
  - name: seo_briefs
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: marketing
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

For a target keyword, produces an SEO brief: intent, competitors, outline, headings, entities to cover, target word count.

## Inspiration

Derived from the Business Operations rollout planner — SEO Briefs cell in the marketing × 2-capture × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `serp_api` | provider-specific | vendor | maybe |
| `keyword_tools` | provider-specific | vendor | maybe |
| `web_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Keyword + SERP.
- **Writes**: SEO brief..
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

- **System**: "You run the SEO Briefs job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
