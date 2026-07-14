---
id: pitch_deck_designer
name: pitch_deck_designer
category: investor-deliverable
phase: 5
step: 39
role: writer
mode: pipeline-stage
depends_on: [executive_summary_writer, financial_excel_builder, gtm_strategist, risk_assessor, fundraising_strategist]
produces: pptx
tools: [read_prior_step, write_pptx]
tags: [pitch-deck, pptx, investor, phase-5]
gate: false
optional: false
---

# pitch_deck_designer

## Identity

```yaml
- name:  pitch_deck_designer
  queue: hermes-agents
  role:  writer
  note:  Investor pitch deck (PPTX) — 12-15 slides synthesizing the whole pipeline.
```

## Purpose

Step 39, only template of Phase 5. Produces the investor pitch deck
(PPTX): 12-15 slides with title, problem, solution, market,
traction, business model, unit economics, GTM, competition, team,
financials, ask. Assets pulled from prior artifacts — nothing new is
researched here.

## Inspiration

`pitch-deck` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |
| `write_pptx(slides)` | python-pptx | — | — |

## Wiring

- **Reads:** steps 34, 35, 30, 33, 37, 38
- **Writes:** `39_pitch_deck.pptx`
- **Upstream:** every prior step
- **Downstream:** external investors

## Structured output

```python
class Slide(BaseModel):
    slide_no: int
    title: str
    body: str
    visual: str | None                     # chart name from step 35 or image asset
    speaker_notes: str

class PitchDeck(BaseModel):
    pptx_path: str                         # 39_pitch_deck.pptx
    slides: list[Slide]
```

## Prompt shape

- **System:** "One idea per slide. Speaker notes carry detail —
  slide face carries the message. System fonts only (Calibri /
  Trebuchet MS). Author = 'Ironbat Digital LLC'."
- **User:** executive summary + financials + GTM + risks +
  (optionally) fundraising plan.

## Extension notes

- If step 37 was skipped, drop the Ask slide or convert it into a
  "next milestones" slide.
- Follow the design-foundations pairing rules — no font embedding.
