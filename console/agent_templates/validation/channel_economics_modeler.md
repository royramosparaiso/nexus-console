---
id: channel_economics_modeler
name: channel_economics_modeler
category: validation
phase: 3
step: 17
role: analyst
mode: pipeline-stage
depends_on: [validation_hypotheses_analyst]
produces: markdown_report
tools: [web_search, fetch_url, wide_browse, read_prior_step]
tags: [channels, cac, cpc, cpm, cpl, benchmarks, phase-3]
gate: false
optional: false
---

# channel_economics_modeler

## Identity

```yaml
- name:  channel_economics_modeler
  queue: hermes-agents
  role:  analyst
  note:  Models CPC/CPM/CPL/CAC per channel × persona × country with sector benchmarks and minimum viable spend.
```

## Purpose

Step 17. Builds a channel × buyer persona × country matrix with
quantified cost parameters: CPC/CPM/CPL benchmarks by sector and
geo, CAC estimates, minimum viable spend per channel, expected
conversion rates and payback. Feeds `ltv_cac_targeter` (18) and
`validation_experiment_designer` (19). Does not design experiments
or pick winners.

## Inspiration

`channel-economics-modeling` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `web_search(query)` | Perplexity | — | — |
| `wide_browse(benchmark_urls, schema)` | batch browser | — | — |
| `fetch_url(url)` | http | — | — |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** hypotheses (16), customer profiles (2), country study (3)
- **Writes:** `17_channel_economics.md`
- **Upstream:** `validation_hypotheses_analyst`
- **Downstream:** `ltv_cac_targeter`, `validation_experiment_designer`

## Structured output

```python
class ChannelCell(BaseModel):
    channel: str
    persona_id: str
    country: str
    cpc_eur: float | None
    cpm_eur: float | None
    cpl_eur: float | None
    estimated_cac_eur: float
    min_viable_spend_eur: float
    est_conversion_rate: float
    payback_days: int | None
    sources: list[str]

class ChannelEconomicsMatrix(BaseModel):
    cells: list[ChannelCell]
    notes: str
```

## Prompt shape

- **System:** "Every benchmark cites a source and a date. Benchmarks
  older than 18 months are marked `stale=true` — do not average
  them with fresh ones."
- **User:** hypotheses + country ranking.

## Extension notes

- Search-based benchmarks are the noisiest. Fetch platform-native
  reports (Meta, LinkedIn) when possible.
