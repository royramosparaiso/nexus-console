# Template card schema

Every template file in this catalogue starts with a YAML frontmatter
block. The frontmatter is the machine-readable contract; the markdown
body below it is the human-readable explanation. Tooling (Agent
Factory UI, discovery API) reads the frontmatter to power search,
category filters and dependency resolution — it must never drift from
the body.

## Two orthogonal axes

The catalogue is organised along **two independent axes**. A card
lives on one axis or both — filters in the UI stack cleanly because
the axes are declared separately.

- **`lifecycle`** — where does this card live in the arc from
  zero to a fundraised company? One of: `project` (pipeline steps
  0-39), `ops` (running-business operations, always-on), `both`,
  `none` (standalone verticals like finance markets).
- **`ops_axis`** — for ops cards, the classification borrowed from
  the Business Operations planner (7 domains × 4 rollout stages × 3
  autonomy levels).

Pipeline cards keep the pre-existing `category / phase / step` fields.
Ops cards add `domain / rollout_stage / autonomy`. Both share
`artifact_type` (agent vs sidecar vs skill), verticals, tools, tags.

## Artifact types

Not every card is an agent. The catalogue supports three:

- **`agent`** — LLM-backed. Produces a reasoned artifact (report,
  decision, draft). Has a role and a mode. Consumes reasoning tokens.
- **`sidecar`** — deterministic worker. Ingests, syncs, watches,
  publishes. No LLM in the hot path (may use one for classification
  offline). Consumes compute, not tokens. Examples: `crm_sync`,
  `portal_sync`, `data_migration`, `email_deliverability_checker`.
- **`skill`** — reusable capability that agents and sidecars call.
  Not a standalone runnable. Examples: `contact_enrichment`,
  `web_scraping`, `email_verification`, `phone_lookup`.

Verticals inherit the same three primitives — a real-estate agency
uses agent + sidecar + skill compositions specific to its ops.

## Frontmatter

```yaml
---
# Identity ------------------------------------------------------------
id: <snake_case_identifier>          # unique across the catalogue
name: <snake_case_identifier>        # matches id; the queue-registration name

# Artifact classification --------------------------------------------
artifact_type: <one of: agent | sidecar | skill>
lifecycle: <one of: project | ops | both | none>

# Pipeline axis (set only when lifecycle in {project, both}) ---------
category: <one of: finance | intake | market-research | mvs | validation | scaling | investor-deliverable | sales | deals | marketing | operations | intelligence | customer | back-office | verticals>
phase: <one of: 0 | 1 | 2 | 3 | 4 | 5 | null>
step: <integer or null>              # pipeline step 0-39, null for ops/finance/verticals

# Ops axis (set only when lifecycle in {ops, both}) ------------------
domain: <one of: sales | deals | marketing | operations | intelligence | customer | back-office | null>
rollout_stage: <one of: 1-foundation | 2-capture | 3-generate | 4-orchestrate | null>
autonomy: <one of: human-led | human-assisted | fully-autonomous | null>
maturity: <integer 1..4>              # dots in the reference UI; 1=nascent, 4=mature

# Applicability -------------------------------------------------------
verticals: [<free-form: real-estate | marketing-agency | nightclub | saas | any | ...>]

# Role and shape ------------------------------------------------------
role: <one of: analyst | judge | debater | reflector | coordinator | writer | reviewer | integrator | worker | connector | classifier | null>
mode: <one of: single-shot | debate | pipeline-stage | gate | reflector | streaming | scheduled | event-driven | null>
depends_on: [<list of template ids that must run before this one>]
produces: <markdown_report | structured_json | pdf | xlsx | pptx | decision | reflection | questionnaire | side_effect | data_sync | enriched_record | null>

# Tooling and search --------------------------------------------------
tools:
  - <tool name>                      # short label, expanded in the body
tags: [<free-form search tags>]
gate: <true | false>
optional: <true | false>
---
```

### Nullability rules

- Pipeline cards (`lifecycle: project`): `category / phase / step`
  required; `domain / rollout_stage / autonomy / maturity` = `null`.
- Ops cards (`lifecycle: ops`): `domain / rollout_stage / autonomy /
  maturity` required; `category` = matching ops domain (e.g. `sales`)
  for directory routing; `phase / step` = `null`.
- Bridge cards (`lifecycle: both`): populate all axes.
- Standalone (`lifecycle: none`, e.g. finance): `category` = `finance`
  or `verticals`; ops fields = `null`; `phase = step = null`.
- Skills (`artifact_type: skill`): `mode = role = null` when the skill
  is a pure capability. It may still declare tools it uses.
- Sidecars (`artifact_type: sidecar`): `role = worker | connector |
  classifier`; `mode = streaming | scheduled | event-driven`.

## Field semantics

- **`id` / `name`** — snake_case, matches the file name (without
  `.md`). Value an operator puts in `DEFAULT_HERMES_AGENTS.name`.
- **`artifact_type`** — see above. Enforced by tests.
- **`lifecycle`** — the axis this card belongs to. Determines which
  other frontmatter fields are required or nulled.
- **`category`** — the top-level directory. Primary discovery filter
  in the UI. Ops domain directories use the domain name.
- **`phase` / `step`** — pipeline coordinates. `null` for ops cards.
- **`domain` / `rollout_stage` / `autonomy` / `maturity`** — ops
  coordinates. `null` for pure-pipeline cards.
  - `rollout_stage` follows the reference planner:
    `1-foundation` (data + company brain) →
    `2-capture` (classify, extract, score) →
    `3-generate` (produce work, take action) →
    `4-orchestrate` (agents, monitoring, loops).
  - `autonomy` indicates the default rollout: `human-led` (a person
    drives it), `human-assisted` (AI drafts, human approves),
    `fully-autonomous` (AI runs unattended).
  - `maturity` (1..4) reflects readiness — 1 is nascent, 4 is
    production-hardened. Matches the dot indicator in the reference UI.
- **`verticals`** — free-form list. `any` means the card is generic
  across verticals; specific values (`real-estate`, `marketing-agency`,
  `nightclub`, `saas`, `restaurant`, …) mean the card is tuned to that
  vertical or introduces vertical-specific behaviour.
- **`role`** — role vocabulary. Sidecars use `worker | connector |
  classifier`. Skills may set `null`.
- **`mode`** — orchestration shape:
  - `single-shot`: one LLM call, structured output
  - `debate`: turn-based multi-agent loop
  - `pipeline-stage`: reads prior stage outputs, writes to workspace
  - `gate`: decision checkpoint, emits go/no-go
  - `reflector`: postmortem / memory writer
  - `streaming`: sidecar consuming a live event stream
  - `scheduled`: sidecar running on a cron cadence
  - `event-driven`: sidecar reacting to webhooks or queue messages
- **`depends_on`** — list of template `id`s whose outputs this card
  consumes. The Agent Factory can auto-order runs from this.
- **`produces`** — the artifact type the template writes. Sidecars
  typically produce `side_effect`, `data_sync`, or `enriched_record`.
- **`tools`** — short labels; the body's "## Tools" table expands
  each into backing endpoint and provider chain.
- **`tags`** — free-form; drive fuzzy search.
- **`gate`** — `true` for templates that emit a formal
  go/no-go/pivot decision.
- **`optional`** — `true` for templates that are conditional.

## Body sections

Agents and pipeline cards keep the eight-section layout:

1. `## Identity`, 2. `## Purpose`, 3. `## Inspiration`, 4. `## Tools`,
5. `## Wiring`, 6. `## Structured output`, 7. `## Prompt shape`,
8. `## Extension notes`.

Sidecars and skills follow a shorter layout, but the first three
sections (`## Identity`, `## Purpose`, `## Wiring`) are mandatory and
are enforced by tests. Sidecars additionally declare
`## Trigger` and `## Side effects`. Skills declare `## Inputs` and
`## Outputs`.
