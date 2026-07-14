---
id: company_deep_dive
name: company_deep_dive
artifact_type: agent
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [web_search, crunchbase, similarweb]
tags: [research, deep-dive]
gate: false
optional: false
---

# company_deep_dive

## Identity

```yaml
agents:
  - name: company_deep_dive
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Produces a company deep-dive: history, funding, product, GTM, tech stack, org, financials, competitive position.

## Inspiration

Derived from the Business Operations rollout planner — Company Deep-Dive cell in the intelligence × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `crunchbase` | provider-specific | vendor | maybe |
| `similarweb` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Company name.
- **Writes**: Deep-dive report..
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

- **System**: "You run the Company Deep-Dive job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
