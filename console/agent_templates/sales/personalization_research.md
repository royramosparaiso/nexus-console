---
id: personalization_research
name: personalization_research
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [web_search, fetch_url, read_crm]
tags: [personalization, research, hooks]
gate: false
optional: false
---

# personalization_research

## Identity

```yaml
agents:
  - name: personalization_research
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

For a target contact + account, mines recent posts, blog articles, press mentions and job changes to produce personalization hooks per message.

## Inspiration

Derived from the Business Operations rollout planner — Personalization Research cell in the sales × 1-foundation × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search` | provider-specific | vendor | maybe |
| `fetch_url` | provider-specific | vendor | maybe |
| `read_crm` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Contact + account records.
- **Writes**: Personalization brief per contact..
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

- **System**: "You run the Personalization Research job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
