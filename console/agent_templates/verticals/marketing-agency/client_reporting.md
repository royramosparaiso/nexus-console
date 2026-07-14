---
id: client_reporting
name: client_reporting
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: marketing
rollout_stage: 4-orchestrate
autonomy: fully-autonomous
maturity: 3
verticals: [marketing-agency]
role: writer
mode: scheduled
depends_on: []
produces: pdf
tools: [ga4_api, meta_ads_api, google_ads_api, write_pdf]
tags: [reporting, client, agency]
gate: false
optional: false
---

# client_reporting

## Identity

```yaml
agents:
  - name: client_reporting
    role: writer
    mode: scheduled
    produces: pdf
    domain: marketing
    rollout_stage: 4-orchestrate
    autonomy: fully-autonomous
```

## Purpose

Monthly client report: KPIs, wins, spend, next month plan — auto-personalised per client brand.

## Inspiration

Derived from the Business Operations rollout planner — Client Reporting cell in the marketing × 4-orchestrate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `ga4_api` | provider-specific | vendor | maybe |
| `meta_ads_api` | provider-specific | vendor | maybe |
| `google_ads_api` | provider-specific | vendor | maybe |
| `write_pdf` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Client accounts data.
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

- **System**: "You run the Client Reporting job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
