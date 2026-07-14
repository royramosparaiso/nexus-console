---
id: re_valuation_analyst
name: re_valuation_analyst
artifact_type: agent
lifecycle: ops
category: verticals
phase: null
step: null
domain: intelligence
rollout_stage: 3-generate
autonomy: human-assisted
maturity: 2
verticals: [real-estate]
role: analyst
mode: single-shot
depends_on: [re_comparables_valuation]
produces: markdown_report
tools: [read_crm, comparables_source]
tags: [valuation, comparables, decision-support, real-estate]
gate: false
optional: false
---

# re_valuation_analyst

## Identity

```yaml
agents:
  - name: re_valuation_analyst
    role: analyst
    mode: single-shot
    produces: markdown_report
    domain: intelligence
    rollout_stage: 3-generate
    autonomy: human-assisted
    verticals: [real-estate]
```

## Purpose

Valuation & comparables analyst. Produces a **decision-support** valuation range with the comparables and assumptions behind it. This is not a certified appraisal (tasación) and does not replace one.

## Inspiration

Real-estate-agency vertical adapter. Composes generic ops skills/sidecars with real-estate-specific behaviour; see the `real_estate` workflows for how this agent participates end to end.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_crm` | provider-specific | vendor | maybe |
| `comparables_source` | provider-specific | vendor | maybe |

Credentials for these tools are referenced only as `${VAR}` and live in `nexus.secrets.env` (0600, gitignored). No secret is ever hard-coded in a template.

## Wiring

- **Reads**: Subject property facts + retrieved comparable listings/transactions.
- **Writes**: A valuation-range report: low/mid/high, comps table, assumptions, caveats.
- **Upstream**: Comparables retrieval skill and listing acquisition manager.
- **Downstream**: Listing acquisition / pricing conversation with the seller (human-led).
- **Depends on**: `re_comparables_valuation`

## Structured output

```python
class Output(BaseModel):
    summary: str
    findings: list[str]
    next_actions: list[str]
    confidence: float
```

## Prompt shape

- **System**: "You run the re_valuation_analyst role for a real-estate agency. Return concise, decision-ready output. Never invent market data, prices or legal/compliance conclusions."
- **User**: injected context bundle + the specific ask.

## Extension notes

- Explicitly labels output as informational. No market price is invented; every figure traces to a comparable or a configurable assumption (`${VALUATION_ASSUMPTIONS_REF}`).
- All names, offices, agent codes, numbers and performance figures used in examples are **illustrative** and fictional — never real market data, and never a compliance, legal, valuation or financial guarantee.
