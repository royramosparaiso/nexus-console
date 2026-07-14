---
id: framework_bridge
name: framework_bridge
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [integration_profile, framework_service]
tags: [framework, langchain, llamaindex, haystack, txtai, sidecar, mcp, integration, skill]
gate: false
optional: true
---

# framework_bridge

## Identity

```yaml
skills:
  - name: framework_bridge
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: reach an orchestration framework — LangChain, LlamaIndex,
Haystack, or txtai — as an **external service** (an HTTP/MCP sidecar the
operator runs), not as an LLM provider. Nexus does not import these libraries;
it stores a connection profile to a running framework service and calls its
health/capability contract.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `framework_service` | framework HTTP/MCP sidecar | external | optional env-ref |

## Inputs

A `framework` adapter (`fw_langchain`, `fw_llamaindex`, `fw_haystack`,
`fw_txtai`) and a connection profile pointing `base_url` at the running sidecar.

## Outputs

Framework invocation results as `structured_json` plus an HTTP health probe
state.

## Wiring

Configure on **Ecosystem → Integrations**. These adapters carry a
`framework_bridge` template link so a profile can be scoped to this card via
`template_ids`, and resolved with
`GET /integrations/resolve?template_id=framework_bridge`.

## Safety limits

- **Not an LLM provider.** Framework bridges orchestrate; they do not substitute
  for [`llm_provider`](llm_provider.md) credentials.
- **Operator-run sidecar.** The framework process is external and local/
  self-hosted; Nexus imposes no cloud dependency and vendors no framework code.
- **Health-gated.** A bridge is `configurable` until its `/health` probe passes.
