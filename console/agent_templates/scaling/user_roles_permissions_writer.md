---
id: user_roles_permissions_writer
name: user_roles_permissions_writer
category: scaling
phase: 4
step: 25
role: writer
mode: pipeline-stage
depends_on: [functional_specifier]
produces: markdown_report
tools: [read_prior_step]
tags: [rbac, roles, permissions, iam, phase-4]
gate: false
optional: false
---

# user_roles_permissions_writer

## Identity

```yaml
- name:  user_roles_permissions_writer
  queue: hermes-agents
  role:  writer
  note:  RBAC/ABAC model — roles, permissions, resource scopes, admin/tenant separation.
```

## Purpose

Step 25. Defines the identity/authorization model: roles,
permission matrix per resource, admin vs tenant separation,
delegated administration, service accounts, invite/onboarding
flows and audit surface. Feeds implementation (`data_schema` and
`platform_areas`).

## Inspiration

`user-roles-permissions` skill.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `read_prior_step(step)` | filesystem | — | — |

## Wiring

- **Reads:** step 24
- **Writes:** `25_user_roles_permissions.md`
- **Upstream:** `functional_specifier`
- **Downstream:** `data_schema_designer`, `platform_areas_architect`

## Structured output

```python
class Role(BaseModel):
    role: str
    description: str
    default_scopes: list[str]

class Permission(BaseModel):
    resource: str
    role: str
    actions: list[str]                     # create, read, update, delete, invite, ...
    conditions: str | None

class RolesPermissionsModel(BaseModel):
    roles: list[Role]
    permissions: list[Permission]
    admin_separation: str
    audit_events: list[str]
```

## Prompt shape

- **System:** "Every action a user can trigger via the UI has a
  matching permission entry. If a UI story exists with no
  permission, one of them is wrong."
- **User:** functional specs + personas.

## Extension notes

- Emit an audit-event list — reused by step 33 (risk assessment).
