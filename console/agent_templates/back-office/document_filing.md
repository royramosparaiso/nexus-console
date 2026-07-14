---
id: document_filing
name: document_filing
artifact_type: sidecar
lifecycle: ops
category: back-office
phase: null
step: null
domain: back-office
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: worker
mode: event-driven
depends_on: []
produces: side_effect
tools: [read_pdf, vault_api]
tags: [filing, documents]
gate: false
optional: false
---

# document_filing

## Identity

```yaml
sidecars:
  - name: document_filing
    role: worker
    mode: event-driven
    produces: side_effect
    domain: back-office
    rollout_stage: 2-capture
    autonomy: fully-autonomous
```

## Purpose

Auto-files inbound documents (invoices, contracts, receipts) into the right vault folders with metadata.

## Trigger

Sidecar reacts to webhooks or queue messages.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_pdf` | provider-specific | vendor | maybe |
| `vault_api` | provider-specific | vendor | maybe |

## Wiring

- **Reads**: Document intake queue.
- **Writes**: Filed docs + metadata..

## Side effects

- Emits side_effect to the downstream bus / target system.
- No LLM reasoning in the hot path — any classification happens offline against cached models.
- Idempotent by design: replaying the same event must not double-write.

## Extension notes

- Add rate-limits per provider and back-off on 429/5xx.
- Emit structured logs for the monitoring sidecar to consume.
