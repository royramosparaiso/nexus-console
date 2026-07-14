---
id: person_research
name: person_research
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
tools: [linkedin_api, web_search]
tags: [person, dossier, research]
gate: false
optional: false
---

# person_research

## Identity

```yaml
agents:
  - name: person_research
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

For a target person, builds a dossier: role history, education, public writing, talks, network overlap.

## Inspiration

Derived from the Business Operations rollout planner — Person Research cell in the intelligence × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |
| `web_search` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Person + LinkedIn + web.
- **Writes**: Person dossier..
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

- **System**: "You run the Person Research job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
