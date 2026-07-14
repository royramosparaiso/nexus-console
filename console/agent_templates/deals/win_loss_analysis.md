---
id: win_loss_analysis
name: win_loss_analysis
artifact_type: agent
lifecycle: ops
category: deals
phase: null
step: null
domain: deals
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 2
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: markdown_report
tools: [read_crm, read_calls]
tags: [win-loss, postmortem]
gate: false
optional: false
---

# win_loss_analysis

## Identity

```yaml
agents:
  - name: win_loss_analysis
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: deals
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Post-mortem on closed deals — reason codes, sales-cycle length, competitor mentions, product-gap tallies.

## Inspiration

Derived from the Business Operations rollout planner — Win/Loss Analysis cell in the deals × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `read_calls` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Closed deals + call transcripts.
- **Writes**: Win/loss report..
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

- **System**: "You run the Win/Loss Analysis job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
