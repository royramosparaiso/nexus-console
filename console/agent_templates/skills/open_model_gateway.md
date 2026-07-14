---
id: open_model_gateway
name: open_model_gateway
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: [llm_provider]
produces: structured_json
tools: [integration_profile, ollama_runtime, huggingface_inference]
tags: [open-model, phi4, gemma3, llama4, qwen3, ollama, huggingface, local, integration, skill]
gate: false
optional: true
---

# open_model_gateway

## Identity

```yaml
skills:
  - name: open_model_gateway
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: run open-weight model families — Phi-4, Gemma 3, Llama 4,
Qwen 3 — through a real local runtime rather than pretending they are hosted
cloud APIs. The adapters route to an OpenAI-compatible endpoint (Ollama by
default at `http://localhost:11434/v1`) so the same chat contract as
[`llm_provider`](llm_provider.md) applies. Hugging Face Inference is offered for
hosted open models. Nexus never bundles or copies model weights into the repo.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `ollama_runtime` | Ollama OpenAI-compatible `/v1` | external (local) | none |
| `huggingface_inference` | HF Inference API | external | env-ref |

## Inputs

An `open_model_access` adapter (`open_phi4`, `open_gemma3`, `open_llama4`,
`open_qwen3`, `open_huggingface`) and a connection profile. Local families
require a running runtime endpoint; the operator points `base_url` at it.

## Outputs

Model responses as `structured_json` plus a probe state. Local runtimes report
`unreachable` until the operator starts Ollama (or an equivalent
OpenAI-compatible server) and pulls the model.

## Wiring

Configure on **Ecosystem → Integrations**: the local families default to the
Ollama endpoint and carry the `local` tag; `open_huggingface` uses an
`HF_TOKEN` env reference. Health via
`POST /integrations/profiles/{id}/test` (OpenAI-compatible `/models` probe).

## Safety limits

- **No fake cloud API.** Phi/Gemma/Llama/Qwen are represented as a runtime
  endpoint, never as a direct first-party cloud key.
- **No bundled weights.** Models are pulled by the operator's runtime; the repo
  ships only the connection descriptor.
- **License awareness.** Each open-weight family carries its own license; the
  operator is responsible for accepting it in their runtime.
