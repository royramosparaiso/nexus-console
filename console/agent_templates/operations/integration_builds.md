---
id: integration_builds
name: integration_builds
artifact_type: agent
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [fetch_url, read_api_docs]
tags: [integration, api, spec]
gate: false
optional: false
---

# integration_builds

## Identity

```yaml
agents:
  - name: integration_builds
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: operations
    rollout_stage: 3-generate
    autonomy: human-assisted
```

## Purpose

Drafts integration specs against third-party APIs — auth, endpoints, quotas, error paths, test plan.

## Inspiration

Derived from the Business Operations rollout planner — Integration Builds cell in the operations × 3-generate × human-assisted matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `fetch_url` | provider-specific | vendor | maybe |
| `read_api_docs` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: API docs + use case.
- **Writes**: Integration spec..
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

- **System**: "You run the Integration Builds job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
