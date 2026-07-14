---
id: cold_call_scripting
name: cold_call_scripting
artifact_type: agent
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 2
verticals: [any]
role: writer
mode: single-shot
depends_on: []
produces: markdown_report
tools: [playbook_reader, objection_library_query]
tags: [cold-call, script, sdr]
gate: false
optional: false
---

# cold_call_scripting

## Identity

```yaml
agents:
  - name: cold_call_scripting
    role: writer
    mode: single-shot
    produces: markdown_report
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Produces a cold-call script skeleton: opener, pain question, value pivot, objection turns, CTA — tuned to persona and vertical.

## Inspiration

Derived from the Business Operations rollout planner — Cold-Call Scripting cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `playbook_reader` | provider-specific | vendor | maybe |
| `objection_library_query` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: ICP + persona + product one-pager.
- **Writes**: Call script with branching tree..
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

- **System**: "You run the Cold-Call Scripting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
