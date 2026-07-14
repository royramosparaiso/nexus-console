---
id: project_intake_facilitator
name: project_intake_facilitator
category: intake
phase: 0
step: 0
role: writer
mode: single-shot
depends_on: []
produces: questionnaire
tools: [read_attachment, extract_pdf_text, extract_docx_text, fetch_url, write_docx]
tags: [intake, questionnaire, founder-onboarding, docx]
gate: false
optional: false
---

# project_intake_facilitator

## Identity

```yaml
- name:  project_intake_facilitator
  queue: hermes-agents
  role:  writer
  note:  Generates the Project Intake Questionnaire DOCX, pre-filled from any source material the founder provides.
```

## Purpose

Step 0 of the project-analysis pipeline. Produces a single DOCX with
six required sections (identity, problem, customer segments, product
status, team and resources, capital and tranches) and five optional
sections (competition, pricing, legal, fundraising, tech stack). If
the founder provides source material — text dump, URLs, attached PDF
/ DOCX / MD, or any combination — the agent reads all of it and
pre-fills every field with an inferred answer. Contradictions between
sources are flagged inline with a `CONFLICT` badge, not silently
merged.

## Inspiration

`project-intake-questionnaire` skill (user library).

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_attachment(path)` | filesystem | — | — |
| `extract_pdf_text(path)` | pdfplumber | — | — |
| `extract_docx_text(path)` | python-docx | — | — |
| `fetch_url(url)` | http | — | — |
| `write_docx(sections, path)` | python-docx | — | — |

## Wiring

- **Reads:** `intake_sources` (list of file paths / URLs), `founder_text`
- **Writes:** `intake_questionnaire_docx` (path), `intake_conflicts` (list)
- **Upstream:** none
- **Downstream:** every Phase 1 template reads the filled questionnaire

## Structured output

```python
class IntakeConflict(BaseModel):
    section: str
    field: str
    sources: list[str]              # where each conflicting value came from
    values: list[str]

class IntakeResult(BaseModel):
    docx_path: Path
    fields_prefilled: int
    fields_blank: int
    conflicts: list[IntakeConflict]
```

## Prompt shape

- **System:** "You produce a Project Intake Questionnaire. You never
  invent facts. If a section has no source data, leave it blank and
  count it in `fields_blank`. If two sources disagree, list both with
  a `CONFLICT` badge — do not choose."
- **User:** interpolates the list of attached sources and any
  free-text the founder pasted.

## Extension notes

- If the founder pastes contradictory numbers (e.g. "we have 3
  founders" in text vs "2 founders" in an attached deck), the DOCX
  gets both values and the pipeline downstream must resolve — do not
  hide the discrepancy.
- The DOCX is the pipeline's shared source of truth. Every downstream
  template should read from the same file, not from the raw founder
  chat.
