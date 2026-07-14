---
id: strategic_decision_gate
name: strategic_decision_gate
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 10
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: judge
mode: gate
depends_on: [market_gap_analyst, swot_analyst]
produces: decision
tools: [read_prior_step, write_pivot_folder]
tags: [gate, checkpoint, go-no-go, pivot, phase-1, phase-boundary]
gate: true
optional: false
---

# strategic_decision_gate

## Identity

```yaml
- name:  strategic_decision_gate
  queue: hermes-agents
  role:  judge
  note:  Synthesises Phase-1 into a traffic-light go/no-go/pivot decision. If pivot, creates a versioned project folder.
```

## Purpose

Step 10, final gate of Phase 1. Reads every Phase-1 output and emits
a decision across 6 dimensions (market, competition, timing,
customer fit, pricing viability, identified gap). Recommends **GO**,
**PIVOT** or **ABANDON**. On PIVOT, creates a versioned folder,
writes a pivot proposal and preserves prior analysis as reference.
On ABANDON, writes a lessons-learned document.

## Inspiration

`strategic-decision-checkpoint` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |
| `write_pivot_folder(pivot_id, prior_paths)` | filesystem | — | — |

## Wiring

- **Reads:** all Phase-1 outputs
- **Writes:** `10_strategic_decision_checkpoint.md` + optional pivot folder
- **Upstream:** every Phase-1 template
- **Downstream:** all Phase-2 templates (only if GO)

## Structured output

```python
class DimensionScore(BaseModel):
    dimension: Literal["market", "competition", "timing", "customer_fit", "pricing_viability", "identified_gap"]
    light: Literal["green", "yellow", "red"]
    rationale: str

class StrategicDecision(BaseModel):
    scores: list[DimensionScore]
    verdict: Literal["GO", "PIVOT", "ABANDON"]
    justification: str
    pivot_proposal: str | None
    lessons_learned: str | None
```

## Prompt shape

- **System:** "You are the gate. Two red lights or three yellows
  force at minimum a PIVOT. You do not let founder enthusiasm
  override the record."
- **User:** all Phase-1 paths.

## Extension notes

- Downstream templates must not run when `verdict != "GO"`. The
  coordinator enforces this by short-circuiting.
- Pivot folder naming: `pivot_YYYYMMDD_<slug>/`.
