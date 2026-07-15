---
id: web_extraction
name: web_extraction
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: intelligence
rollout_stage: 2-capture
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [integration_profile, extraction_service]
tags: [data-extraction, crawl4ai, firecrawl, scrapegraphai, megaparser, docling, llamaparse, extractthinker, integration, skill]
gate: false
optional: true
---

# web_extraction

## Identity

```yaml
skills:
  - name: web_extraction
    kind: skill
    produces: structured_json
    domain: intelligence
```

## Purpose

Reusable capability: crawl, scrape, and parse documents/web pages into
structured data via a chosen extraction backend — Crawl4AI, Firecrawl,
ScrapeGraphAI, MegaParser, Docling, LlamaParse, or ExtractThinker. Each maps to
its real operating model: an operator-run HTTP/MCP sidecar (self-hosted tools)
or a hosted API key (Firecrawl, LlamaParse). No scraper library is vendored.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `integration_profile` | `/integrations/profiles` adapter registry | native | env-ref |
| `extraction_service` | extraction sidecar or hosted API | external | env-ref (hosted) |

## Inputs

A `data_extraction` adapter (`extract_crawl4ai`, `extract_firecrawl`,
`extract_scrapegraphai`, `extract_megaparser`, `extract_docling`,
`extract_llamaparse`, `extract_extractthinker`) and a connection profile.
Self-hosted backends set `base_url`; hosted ones set a key env reference.

## Outputs

Extracted content as `structured_json` plus a probe state (HTTP health for
sidecars, key-presence for hosted APIs like LlamaParse).

## Wiring

Configure on **Ecosystem → Integrations**; enabled profiles expose a
`web_extraction` capability. Feed output into
[`embeddings_provider`](embeddings_provider.md) →
[`vector_store`](vector_store.md) for ingestion.

## Safety limits

- **Respect robots/ToS.** Extraction targets are the operator's responsibility;
  Nexus only brokers the connection.
- **No plaintext secrets.** Hosted-API keys are env-name references.
- **Operator-run by default.** Self-hosted backends run in the operator's
  environment; the repo vendors no scraping code.
