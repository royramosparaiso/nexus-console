---
id: proof_matching
name: proof_matching
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
role: analyst
mode: single-shot
depends_on: []
produces: structured_json
tools: [read_proof_library, score_similarity]
tags: [proof, case-study, social-proof]
gate: false
optional: false
---

# proof_matching

## Identity

```yaml
agents:
  - name: proof_matching
    role: analyst
    mode: single-shot
    produces: structured_json
    domain: sales
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

Matches a target account to the closest 1-3 case studies, quotes and metrics from the proof library.

## Inspiration

Derived from the Business Operations rollout planner — Proof Matching cell in the sales × 3-generate × fully-autonomous matrix.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_proof_library` | provider-specific | vendor | maybe |
| `score_similarity` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Account record + proof library.
- **Writes**: Matched proof set with fit rationale..
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

- **System**: "You run the Proof Matching job. Return concise, decision-ready output. Never invent data."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Tune tools per vertical (see the verticals directory for adapted variants).
- Deliberately keep this card generic across verticals — vertical specialisation lives in `verticals/<slug>/`.
