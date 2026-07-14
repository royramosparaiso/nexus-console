---
id: document_extraction
name: document_extraction
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [read_pdf, read_docx, extract_fields]
tags: [extraction, documents, skill]
gate: false
optional: false
---

# document_extraction

## Identity

```yaml
skills:
  - name: document_extraction
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: from a document (PDF, DOCX, PPTX), extracts structured fields defined by a schema.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_pdf` | provider-specific | vendor | maybe |
| `read_docx` | provider-specific | vendor | maybe |
| `extract_fields` | provider-specific | vendor | maybe |

## Inputs

Document + schema.

## Outputs

Structured record..

## Wiring

Callable by any agent or sidecar in the catalogue. Not runnable on its own.

## Extension notes

- Cache aggressively; every call is billable.
- Return provenance + confidence alongside the value.
