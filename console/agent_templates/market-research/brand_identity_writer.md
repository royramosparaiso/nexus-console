---
id: brand_identity_writer
name: brand_identity_writer
artifact_type: agent
lifecycle: project
category: market-research
phase: 1
step: 7
domain: null
rollout_stage: null
autonomy: null
maturity: null
verticals: [any]
role: writer
mode: pipeline-stage
depends_on: [competitive_analyst, market_customer_profiler]
produces: markdown_report
tools: [read_prior_step, generate_image]
tags: [brand, identity, logo, naming, tone, phase-1]
gate: false
optional: false
---

# brand_identity_writer

## Identity

```yaml
- name:  brand_identity_writer
  queue: hermes-agents
  role:  writer
  note:  Produces the complete Brand Identity Kit — naming, logo guidelines, palette, typography, tone of voice, visual system.
```

## Purpose

Step 7, between competitive-analysis and pricing-strategy. Delivers
a brand kit: naming rationale, logo direction (with generated
concept art), colour palette with HSL values, type pairing, tone of
voice guide (do/don't lists), and applied examples (business card,
landing hero, social avatar).

## Inspiration

`brand-identity-kit` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |
| `generate_image(prompt, style, aspect)` | media generation | — | — |

## Wiring

- **Reads:** `02_market_customer_profiles.md`, `05_competitive_analysis.md`
- **Writes:** `07_brand_identity_kit.md` + generated image assets
- **Upstream:** `competitive_analyst`
- **Downstream:** `pricing_strategist` (positioning reference), `ux_platform_designer`, `pitch_deck_designer`

## Structured output

```python
class BrandKit(BaseModel):
    brand_name: str
    naming_rationale: str
    palette_hsl: dict[str, str]           # role -> "H S% L%"
    typography: dict[Literal["display","body","mono"], str]
    tone_do: list[str]
    tone_dont: list[str]
    logo_concepts: list[Path]             # generated image files
    example_applications: list[Path]
```

## Prompt shape

- **System:** "You derive the brand from the paying buyer, not from
  founder taste. A luxury B2B palette on a low-price SMB product is
  a bug."
- **User:** the customer profiles + competitor positioning.

## Extension notes

- Never use blacklisted display fonts (Papyrus, Comic Sans, Impact,
  etc.). Load `design-foundations` for the full list.
- Generate at least 3 logo directions — the founder picks, the agent
  does not.
