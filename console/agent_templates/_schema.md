# Template card schema

Every template file in this catalogue starts with a YAML frontmatter
block. The frontmatter is the machine-readable contract; the markdown
body below it is the human-readable explanation. Tooling (Agent
Factory UI, discovery API) reads the frontmatter to power search,
category filters and dependency resolution — it must never drift from
the body.

## Frontmatter

```yaml
---
id: <snake_case_identifier>          # unique across the catalogue
name: <snake_case_identifier>        # matches id; the queue-registration name
category: <one of: finance | intake | market-research | mvs | validation | scaling | investor-deliverable>
phase: <one of: 0 | 1 | 2 | 3 | 4 | 5>
step: <integer or null>              # pipeline step number when applicable (0-39), null for finance/misc templates
role: <one of: analyst | judge | debater | reflector | coordinator | writer | reviewer | reflector | integrator>
mode: <one of: single-shot | debate | pipeline-stage | gate | reflector>
depends_on: [<list of template ids that must run before this one>]
produces: <artifact type: markdown_report | structured_json | pdf | xlsx | pptx | decision | reflection | questionnaire>
tools:
  - <tool name>          # short label, expanded in the body
tags: [<free-form search tags>]
gate: <true | false>                 # true for gate/checkpoint templates
optional: <true | false>             # true if the template is conditional
---
```

## Field semantics

- **`id` / `name`** — snake_case, matches the file name (without
  `.md`). This is the value an operator would put in
  `DEFAULT_HERMES_AGENTS.name`.
- **`category`** — the top-level directory. Used as the primary
  discovery filter in the UI.
- **`phase`** — pipeline phase (0=intake, 1=market research, 2=MVS,
  3=validation, 4=scaling, 5=investor deliverable). `null` for
  finance-vertical templates that don't belong to the project-analysis
  pipeline.
- **`step`** — the exact step number in the sequential pipeline (0
  through 39). Templates that don't belong to the pipeline set this to
  `null`.
- **`role`** — matches the Hermes agent role vocabulary
  (`planner`, `coordinator`, `worker`, `analyst`, `judge`, `debater`,
  `reflector`, `writer`, `reviewer`, `integrator`).
- **`mode`** — orchestration shape:
  - `single-shot`: one LLM call, structured output
  - `debate`: turn-based multi-agent loop
  - `pipeline-stage`: reads prior stage outputs, writes to workspace
  - `gate`: decision checkpoint, emits go/no-go
  - `reflector`: postmortem / memory writer
- **`depends_on`** — list of template `id`s whose outputs this
  template consumes. The Agent Factory can auto-order runs from this.
- **`produces`** — the artifact type the template writes.
- **`tools`** — short labels; the body's "## Tools" table expands
  each into backing endpoint and provider chain.
- **`tags`** — free-form; drive fuzzy search.
- **`gate`** — set to `true` for templates that emit a formal
  go/no-go/pivot decision.
- **`optional`** — set to `true` for templates that are conditional
  (e.g. `mobile_app_specifier` only fires when platform architecture
  recommends a mobile app; `startup_valuation_analyst` only fires if
  the founder decides to fundraise).

## Body sections (required in this order)

1. `## Identity` — the same YAML block, but as an `agents:` list ready
   to paste into `DEFAULT_HERMES_AGENTS`.
2. `## Purpose` — one paragraph, plain language.
3. `## Inspiration` — link to the source skill / repo / paper.
4. `## Tools` — table with columns: Tool | Backing | Provider | Key?
5. `## Wiring` — reads / writes / upstream / downstream.
6. `## Structured output` — Pydantic-style schema block.
7. `## Prompt shape` — system + user prompt skeletons.
8. `## Extension notes` — optional; deployment-specific gotchas.

Templates that don't need one of these sections (e.g. gates have no
"Tools" table) may omit it, but the ordering of what remains must not
change. The test suite enforces the presence of Identity / Purpose /
Wiring on every card.
