---
id: data_schema_designer
name: data_schema_designer
category: scaling
phase: 4
step: 28
role: analyst
mode: pipeline-stage
depends_on: [functional_specifier, user_roles_permissions_writer, platform_areas_architect]
produces: markdown_report
tools: [read_prior_step]
tags: [data-model, schema, entities, flows, phase-4]
gate: false
optional: false
---

# data_schema_designer

## Identity

```yaml
- name:  data_schema_designer
  queue: hermes-agents
  role:  analyst
  note:  Logical data model — entities, attributes, relationships, retention policy and cross-area data flows.
```

## Purpose

Step 28. Defines the logical data model that the platform will run
on: entities, attributes, relationships, indexes on hot paths,
retention/archival policy, PII classification, and the primary
data flows across platform areas (who writes what, who reads what,
where events go).

## Inspiration

`data-schema-flows` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** steps 24, 25, 26
- **Writes:** `28_data_schema.md`
- **Upstream:** `functional_specifier`, `user_roles_permissions_writer`, `platform_areas_architect`
- **Downstream:** `tech_stack_vendors_analyst`, `legal_ip_analyst`, `risk_assessor`

## Structured output

```python
class Entity(BaseModel):
    entity: str
    attributes: list[str]
    pii_fields: list[str]
    relationships: list[str]
    retention: str

class DataFlow(BaseModel):
    from_area: str
    to_area: str
    payload: str
    trigger: str

class DataModel(BaseModel):
    entities: list[Entity]
    flows: list[DataFlow]
    high_traffic_indexes: list[str]
```

## Prompt shape

- **System:** "PII is a legal liability, not a schema decoration.
  Every PII field is called out — step 32 will need this."
- **User:** functional specs + permissions + areas.

## Extension notes

- Do NOT emit vendor-specific DDL. The physical schema is chosen
  at step 31 (tech stack).
