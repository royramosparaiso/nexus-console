---
id: re_property_matching_rank
name: re_property_matching_rank
artifact_type: skill
lifecycle: ops
category: verticals
phase: null
step: null
domain: sales
rollout_stage: 2-capture
autonomy: fully-autonomous
maturity: 3
verticals: [real-estate]
role: null
mode: null
depends_on: [re_requirements_normalization]
produces: structured_json
tools: [search_inventory, score_similarity]
tags: [matching, ranking, buyer, skill, real-estate]
gate: false
optional: false
---

# re_property_matching_rank

## Identity

```yaml
skills:
  - name: re_property_matching_rank
    kind: skill
    produces: structured_json
    domain: sales
    verticals: [real-estate]
```

## Purpose

Match and rank inventory against a normalized buyer brief, returning ranked candidates with a per-candidate match rationale.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `search_inventory` | provider-specific | vendor | maybe |
| `score_similarity` | provider-specific | vendor | maybe |

Any credentials are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is hard-coded.

## Inputs

Normalized buyer brief + current inventory.

## Outputs

Ranked candidate list with match reasons and gaps.

## Wiring

Callable by any agent or sidecar in the real-estate vertical. Not runnable on its own.
- **Depends on**: `re_requirements_normalization`

## Extension notes

- Cache where calls are billable; return provenance + confidence alongside values.
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
