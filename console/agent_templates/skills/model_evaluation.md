---
id: model_evaluation
name: model_evaluation
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [integration_profile, evaluation_service]
tags: [evaluation, giskard, ragas, deepeval, testing, sidecar, integration, skill]
gate: false
optional: true
---

# model_evaluation

## Identity

```yaml
skills:
  - name: model_evaluation
    kind: skill
    produces: structured_json
    domain: intelligence
```

## Purpose

Reusable capability: evaluate LLM/RAG output quality and safety through an
evaluation backend run as an operator sidecar. Three adapters cover the
screenshot's evaluation row: Giskard (the one reliably identifiable logo) plus
Ragas and DeepEval as the two widely-used open-source RAG/LLM evaluation
frameworks. Where a logo could not be identified with confidence, a generic
evaluation adapter is used rather than inventing a vendor name.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `evaluation_service` | evaluation sidecar HTTP service | external | optional env-ref |

## Inputs

An `evaluation` adapter (`eval_giskard`, `eval_ragas`, `eval_deepeval`) and a
connection profile pointing `base_url` at the running evaluation service.

## Outputs

Evaluation scores/reports as `structured_json` plus an HTTP health probe state.

## Wiring

Configure on **Ecosystem → Integrations**; enabled profiles expose an
`evaluation` capability for CI-style quality gates on agent output. Pair with
[`llm_provider`](llm_provider.md) and [`vector_store`](vector_store.md) to
score a full RAG pipeline.

## Safety limits

- **Honest identification.** Only Giskard is named from the logo; the other two
  are the well-known open-source frameworks, not invented vendors.
- **Operator-run sidecar.** Evaluation runs in the operator's environment; no
  eval library is vendored into the repo.
- **Health-gated.** An evaluator is `configurable` until its `/health` probe
  passes.
