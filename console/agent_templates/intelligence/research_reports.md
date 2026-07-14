---
id: research_reports
name: research_reports
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
role: writer
mode: single-shot
depends_on: []
produces: pdf
tools: [write_pdf, chart_render]
tags: [report, pdf]
gate: false
optional: false
---

# research_reports

## Identity

```yaml
agents:
  - name: research_reports
    role: writer
    mode: single-shot
    produces: pdf
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Full research-report assembly: cover, exec summary, sections, charts, appendix. PDF output for stakeholders.

## Inspiration

Derived from the Business Operations rollout planner — Research Reports cell in the intelligence × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `write_pdf` | provider-specific | vendor | maybe |
| `chart_render` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Research corpus.
- **Writes**: Report PDF..
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

- **System**: "You run the Research Reports job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
