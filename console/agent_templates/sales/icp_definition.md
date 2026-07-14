---
id: icp_definition
name: icp_definition
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, web_search, read_prior_step]
tags: [icp, targeting, firmographics]
gate: false
optional: false
---

# icp_definition

## Identity

```yaml
agents:
  - name: icp_definition
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 1-foundation
    autonomy: fully-autonomous
```

## Purpose

Derives the Ideal Customer Profile from historical wins, product fit signals and market study — firmographics, technographics, buying triggers.

## Inspiration

Derived from the Business Operations rollout planner — ICP Definition cell in the sales × 1-foundation × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `web_search` | provider-specific | vendor | maybe |
| `read_prior_step` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Customer records, win/loss notes, product docs.
- **Writes**: ICP definition markdown + tags for downstream targeting..
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

- **System**: "You run the ICP Definition job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
