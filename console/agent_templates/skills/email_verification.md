---
id: email_verification
name: email_verification
artifact_type: skill
lifecycle: ops
category: sales
phase: null
step: null
domain: sales
rollout_stage: 1-foundation
autonomy: fully-autonomous
maturity: 4
verticals: [any]
role: null
mode: null
depends_on: []
produces: enriched_record
tools: [neverbounce, zerobounce, smtp_probe]
tags: [email, verification, skill, deliverability]
gate: false
optional: false
---

# email_verification

## Identity

```yaml
skills:
  - name: email_verification
    kind: skill
    produces: enriched_record
    domain: sales
```

## Purpose

Reusable capability: SMTP+MX+catchall verification with confidence score.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `neverbounce` | provider-specific | vendor | maybe |
| `zerobounce` | provider-specific | vendor | maybe |
| `smtp_probe` | provider-specific | vendor | maybe |

## Inputs

Email address.

## Outputs

Verification result: valid | risky | invalid + reason..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
