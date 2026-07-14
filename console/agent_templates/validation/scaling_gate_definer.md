---
id: scaling_gate_definer
name: scaling_gate_definer
category: validation
phase: 3
step: 21
role: judge
mode: gate
depends_on: [ltv_cac_targeter, validation_experiment_designer, tranche_1_budgeter]
produces: decision
tools: [read_prior_step]
tags: [gate-1, scaling, checkpoint, cac-ltv, phase-3, phase-boundary]
gate: true
optional: false
---

# scaling_gate_definer

## Identity

```yaml
- name:  scaling_gate_definer
  queue: hermes-agents
  role:  judge
  note:  Defines the five numerical Gate-1 thresholds that must all be met to authorize Tramo 2 (scaling).
```

## Purpose

Step 21, final gate of Phase 3. Defines the formal Gate 1 criteria:
- **CAC ≤ target**
- **LTV ≥ target**
- **Conversion rate ≥ minimum**
- **Payback period ≤ maximum**
- **Replicability across ≥ N channels**

All five must be simultaneously satisfied to authorize Tramo 2
scaling capital and Phase 4 execution. On PASS, greenlights Phase
4. On FAIL, produces a structured pivot-or-stop framework.

## Inspiration

`scaling-gate-definition` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 18, 19, 20
- **Writes:** `21_scaling_gate.md`
- **Upstream:** `ltv_cac_targeter`, `validation_experiment_designer`, `tranche_1_budgeter`
- **Downstream:** every Phase-4 template (only if PASS)

## Structured output

```python
class GateCriterion(BaseModel):
    criterion: Literal["cac", "ltv", "cvr", "payback", "replicability"]
    threshold: float
    measured: float | None                 # populated at gate evaluation, not at definition
    passed: bool | None

class ScalingGate(BaseModel):
    criteria: list[GateCriterion]
    verdict: Literal["DEFINED", "PASS", "FAIL", "PENDING"]
    pivot_framework: str | None
```

## Prompt shape

- **System:** "All five criteria are ANDed, not averaged. A stellar
  CAC with a 90-day payback still fails the gate if payback max was
  60."
- **User:** LTV/CAC targets + experiment plan + Tramo 1 budget.

## Extension notes

- On DEFINED, the coordinator waits for step-19 experiments to
  complete, then reruns this template with measured values to reach
  PASS / FAIL.
- Any downstream Phase-4 template must refuse to run when
  `verdict != "PASS"`.
