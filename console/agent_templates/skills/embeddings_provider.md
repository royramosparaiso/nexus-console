---
id: embeddings_provider
name: embeddings_provider
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
depends_on: []
produces: structured_json
tools: [integration_profile, embeddings_endpoint]
tags: [embeddings, nomic, sbert, openai, voyage, google, cohere, integration, skill]
gate: false
optional: true
---

# embeddings_provider

## Identity

```yaml
skills:
  - name: embeddings_provider
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: produce text embeddings through one normalised interface
covering Nomic, SentenceTransformers/SBERT, OpenAI, Voyage AI, Google, and
Cohere. Hosted providers use an HTTP endpoint + key reference; local families
(SBERT, Nomic) declare a sidecar/runtime endpoint rather than bundling models
into the repo.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `embeddings_endpoint` | provider embeddings API or local sidecar | external | env-ref |

## Inputs

An `embeddings` adapter (`embed_nomic`, `embed_sbert`, `embed_openai`,
`embed_voyage`, `embed_google`, `embed_cohere`) and a connection profile.
Local SBERT/Nomic require a declared sidecar `base_url`.

## Outputs

Embedding vectors as `structured_json` plus a probe state. Providers with only
a key (e.g. Voyage) report `secret_missing` vs `reachable` via a key-presence
check; endpoint-based ones probe an HTTP health path.

## Wiring

Configure on **Ecosystem → Integrations**. Resolution via
`GET /integrations/capabilities` exposes the `embedding` capability to agents
and vector-store ingestion pipelines. Pair with
[`vector_store`](vector_store.md) to build a retrieval stack.

## Safety limits

- **No bundled models.** Local embedders run in an operator-provided sidecar.
- **No plaintext secrets.** Keys are env-name references, read server-side only.
- **Dimension honesty.** The adapter records the provider; agents must match
  embedding dimensions to their vector store — Nexus does not silently coerce.
