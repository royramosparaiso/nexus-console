---
id: project_scaffolding
name: project_scaffolding
artifact_type: sidecar
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 3-generate
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: connector
mode: event-driven
depends_on: []
produces: side_effect
tools: [github_api, notion_api, slack_api]
tags: [scaffolding, kickoff, provisioning]
gate: false
optional: false
---

# project_scaffolding

## Identity

```yaml
sidecars:
  - name: project_scaffolding
    role: connector
    mode: event-driven
    produces: side_effect
    domain: operations
    rollout_stage: 3-generate
    autonomy: fully-autonomous
```

## Purpose

On project kickoff, provisions the workspace: repo, folder tree, base docs, chat channel, project management board.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `github_api` | provider-specific | vendor | maybe |
| `notion_api` | provider-specific | vendor | maybe |
| `slack_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Project template + client info.
- **Writes**: Provisioned workspace..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
