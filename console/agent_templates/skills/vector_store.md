---
id: vector_store
name: vector_store
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
depends_on: [embeddings_provider]
produces: structured_json
tools: [integration_profile, vector_index]
tags: [vector-db, chroma, pinecone, qdrant, weaviate, milvus, pgvector, cassandra, opensearch, integration, skill]
gate: false
optional: true
---

# vector_store

## Identity

```yaml
skills:
  - name: vector_store
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: connect to a vector/search store for retrieval-augmented
workflows. One adapter family covers Chroma, Pinecone, Qdrant, Weaviate,
Milvus, PostgreSQL/pgvector, Cassandra, and OpenSearch. Each is a typed
connection profile with a provider-appropriate health probe — no client SDK is
vendored.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `vector_index` | store REST/HTTP or DSN connection | external | env-ref |

## Inputs

A `vector_db` adapter (`vdb_chroma`, `vdb_pinecone`, `vdb_qdrant`,
`vdb_weaviate`, `vdb_milvus`, `vdb_pgvector`, `vdb_cassandra`,
`vdb_opensearch`) and a connection profile. HTTP stores use `base_url` +
optional header/key; pgvector uses a `PGVECTOR_DSN` reference; OpenSearch uses
basic auth.

## Outputs

Upsert/query results as `structured_json` plus a probe state. Probe strategy
varies by store: HTTP health for Chroma/Weaviate/Milvus, header key for
Pinecone/Qdrant, `SELECT 1` for pgvector, basic auth for OpenSearch.

## Wiring

Configure on **Ecosystem → Integrations**; enabled profiles expose a
`vector_search` capability through `GET /integrations/resolve`. Pair with
[`embeddings_provider`](embeddings_provider.md) and a framework bridge to
assemble a full RAG pipeline.

## Safety limits

- **No plaintext secrets.** Connection strings and keys are env-name references.
- **DSN normalisation.** pgvector DSNs are coerced to the async driver for the
  probe; the probe runs `SELECT 1` only and never mutates data.
- **Honest reachability.** A store is `configurable` until *Test connection*
  succeeds against the operator's endpoint.
