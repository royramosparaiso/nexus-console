---
id: candidate_sourcing
name: candidate_sourcing
artifact_type: agent
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: human-led
maturity: 1
verticals: [any]
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [linkedin_api, read_references]
tags: [hiring, sourcing, founder-led]
gate: false
optional: false
---

# candidate_sourcing

## Identity

```yaml
agents:
  - name: candidate_sourcing
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: back-office
    rollout_stage: 2-capture
    autonomy: human-led
```

## Purpose

Founder-led. Sources candidate shortlists from LinkedIn + referrals + niche communities against a role scorecard.

## Inspiration

Derived from the Business Operations rollout planner — Candidate Sourcing cell in the back-office × 2-capture × human-led matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `linkedin_api` | provider-specific | vendor | maybe |
| `read_references` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Role scorecard.
- **Writes**: Ranked candidate list..
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

- **System**: "You run the Candidate Sourcing job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
