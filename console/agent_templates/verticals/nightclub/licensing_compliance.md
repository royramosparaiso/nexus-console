---
id: licensing_compliance
name: licensing_compliance
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: operations
rollout_stage: 4-orchestrate
autonomy: human-led
maturity: 1
verticals: [nightclub]
role: analyst
mode: scheduled
depends_on: []
produces: markdown_report
tools: [read_registry, noise_meter_api]
tags: [licensing, compliance, founder-led, nightclub]
gate: false
optional: false
---

# licensing_compliance

## Identity

```yaml
agents:
  - name: licensing_compliance
    role: analyst
    mode: scheduled
    produces: markdown_report
    domain: operations
    rollout_stage: 4-orchestrate
    autonomy: human-led
```

## Purpose

Founder-led. Tracks licences, capacity limits, noise readings, staff certifications; alerts on lapses.

## Inspiration

Derived from the Business Operations rollout planner — Licensing Compliance cell in the operations × 4-orchestrate × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_registry` | provider-specific | vendor | maybe |
| `noise_meter_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Licence registry + logs.
- **Writes**: Compliance state..
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

- **System**: "You run the Licensing Compliance job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
