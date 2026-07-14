---
id: llm_provider
name: llm_provider
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
tools: [integration_profile, openai_compatible_chat]
tags: [llm, chat, openai, anthropic, gemini, mistral, bedrock, cohere, groq, together, integration, skill]
gate: false
optional: true
---

# llm_provider

## Identity

```yaml
skills:
  - name: llm_provider
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: talk to a chat/completion LLM through a single,
OpenAI-compatible contract instead of a bespoke SDK per vendor. One integration
profile covers OpenAI, Anthropic (Claude), Google Gemini, Mistral, Amazon
Bedrock, DeepSeek, Cohere, Groq, Together AI, and any self-hosted
OpenAI-compatible gateway. Nexus does **not** vendor any provider SDK — it
stores a typed connection profile (endpoint + secret env-name references) and
speaks HTTP.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `openai_compatible_chat` | provider `/chat/completions` (or vendor-native) | external | env-ref |

## Inputs

An `adapter_id` from the `llm` category (e.g. `llm_openai`, `llm_anthropic`,
`llm_gemini`) plus a connection profile: optional `base_url` override and secret
references by environment-variable name. No key values are ever entered in the
UI or persisted.

## Outputs

Model responses as `structured_json`, plus a health/probe state
(`reachable` / `unreachable` / `secret_missing` / `no_probe`) surfaced by the
adapter's connection test.

## Wiring

Configure on **Ecosystem → Integrations**: pick an `llm` adapter, set the
endpoint and secret env references, then run *Test connection*. Enabled profiles
are exposed to agents via:

- `GET /integrations/adapters?category=llm` — the catalogue (fields + secret
  env names; never values).
- `POST /integrations/profiles/{id}/test` — provider health probe.
- `GET /integrations/capabilities` / `GET /integrations/resolve` — enabled chat
  capabilities for runtime resolution (secrets redacted to presence flags).

## Safety limits

- **No plaintext secrets.** Keys are referenced by env-var name and read
  server-side only at probe/resolve time; they are never stored or returned.
- **Honest status.** A provider is `configurable` until a working runtime path
  is enabled and tested — the UI never fakes `available`.
- **Bedrock caveat.** Amazon Bedrock uses SigV4, not a bearer key, so its probe
  is `no_probe` (config-only) until an operator wires regional credentials.
