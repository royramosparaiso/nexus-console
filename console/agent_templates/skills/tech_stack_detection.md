---
id: tech_stack_detection
name: tech_stack_detection
artifact_type: skill
lifecycle: ops
category: intelligence
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [builtwith, wappalyzer, read_jobs]
tags: [tech-stack, skill]
gate: false
optional: false
---

# tech_stack_detection

## Identity

```yaml
skills:
  - name: tech_stack_detection
    kind: skill
    produces: structured_json
    domain: intelligence
```

## Purpose

Reusable capability: detects a company's tech stack from web pages, job postings and public repos.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `builtwith` | provider-specific | vendor | maybe |
| `wappalyzer` | provider-specific | vendor | maybe |
| `read_jobs` | provider-specific | vendor | maybe |

## Inputs

Company domain + jobs pages.

## Outputs

Detected stack..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
