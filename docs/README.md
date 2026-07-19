# Documentación de Nexus Console / NexusOS

Índice de la documentación del repositorio. La documentación del **portal gestionado** (Hub, Operator,
Runtime, Registry) es **diseño aprobado, no implementado** (TARGET-STATE, versión de arquitectura
`v1alpha1`). La capa de producto **Personal + Hub por suscripción** (ediciones, entitlements,
suscripción, acceso a paquetes, modalidades de despliegue) es **diseño aprobado, no implementado**
(TARGET-STATE, versión `v1alpha2`, aditiva sobre `v1alpha1`).

## Producto Personal + Hub (`v1alpha2`) — diseño aprobado, no implementado

- [Visión: Personal + Hub por suscripción](vision/nexus-os-vision-personal-hub-subscription.md) —
  ediciones, audiencias, propuesta de valor, fronteras, monetización, acceso a paquetes, modalidades,
  ciclo de vida ante expiración, promesa OSS y no-objetivos; estado actual vs objetivo.
- [Especificaciones (a–j)](specs/README.md) — Personal Runtime, Hub, Team/Org, Operator, Registry,
  modelo de paquetes, entitlements/suscripción/degradación, seguridad/firma/secretos, Studio y
  modalidades de despliegue.
- [ADR-0009 — Ediciones, entitlements y degradación de suscripción](adr/0009-editions-entitlements-and-subscription-degradation.md)
- [ADR-0010 — Separación edición vs modalidad de despliegue](adr/0010-edition-vs-deployment-modality.md)
- Esquemas: [`v1alpha2/`](schemas/v1alpha2/) · Ejemplos válidos e inválidos: [`examples/`](schemas/examples/).

## Portal Gestionado (`v1alpha1`) — diseño aprobado, no implementado

### Visión y arquitectura
- [Visión: extensión Portal Gestionado](vision/nexus-os-vision-managed-portal.md) — incorpora la
  arquitectura de cuatro partes a la Visión de Nexus OS; marca estado actual vs objetivo.
- [Especificación de arquitectura del Portal Gestionado](architecture/managed-platform-architecture.md)
  — contexto, journeys, máquina de estados, modelo de datos, API/eventos, ciclo de vida de packs,
  amenazas, observabilidad, fallos/DR, roadmap y MVP.
- [Glosario formal](architecture/glossary.md) — Hub, Operator, Runtime, Registry, Instance, Blueprint,
  SetupPlan/Task, Area, Agent, Skull/Agent Cognition Profile, Sidecar, Flow, Pack, Overlay, Desired
  State, Installation.
- [Migración y compatibilidad](architecture/migration-and-compatibility.md) — qué pasa con Console/Fly,
  wizard/handoff, plantillas de agente y v0.13.8. Opt-in, no destructiva, reversible.
- [Frontera OSS/comercial y pricing](architecture/product-oss-boundary.md).

### Architecture Decision Records (ADR)
- [ADR-0001 — División Hub/Operator/Runtime/Registry](adr/0001-hub-operator-runtime-registry-split.md)
- [ADR-0002 — Firma y verificación](adr/0002-signing-and-verification.md)
- [ADR-0003 — Contratos Blueprint y SetupPlan](adr/0003-blueprint-and-setup-plan-contracts.md)
- [ADR-0004 — Enrolamiento del Operator e identidad](adr/0004-operator-enrollment-and-identity.md)
- [ADR-0005 — Secrets bundle, OAuth y prohibición en prompts cowork](adr/0005-secrets-bundle-and-oauth.md)
- [ADR-0006 — Formato `nexus.pack.yaml`](adr/0006-nexus-pack-format.md)
- [ADR-0007 — Canales de actualización y rollout](adr/0007-update-channels-and-rollout.md)
- [ADR-0008 — Frontera OSS/comercial y licencia](adr/0008-oss-commercial-boundary-and-license.md)
- [ADR-0009 — Ediciones, entitlements y degradación de suscripción](adr/0009-editions-entitlements-and-subscription-degradation.md) (`v1alpha2`)
- [ADR-0010 — Separación edición vs modalidad de despliegue](adr/0010-edition-vs-deployment-modality.md) (`v1alpha2`)

### Esquemas y ejemplos (`v1alpha1` + `v1alpha2`)
- [Índice de esquemas](schemas/README.md) — JSON Schema 2020-12.
- Esquemas: [`v1alpha1/`](schemas/v1alpha1/) · [`v1alpha2/`](schemas/v1alpha2/) · Ejemplos: [`examples/`](schemas/examples/) (válidos e [`invalid/`](schemas/examples/invalid/)).
- Validación: `console/tests/test_managed_platform_schemas.py` (ambas versiones + fixtures negativos + invariantes).

## Documentos existentes
- [RFC-002 — Protocolo Console ↔ Platform](rfc/002-console-platform-protocol.md).
- [Changelog de documentación y contratos](CHANGELOG.md) — transición `v1alpha1` → `v1alpha2`.

> La Visión canónica de Nexus OS y RFC-001 viven en el repositorio `ironbat-jarvis` (Nexus Platform).
> Ver la [nota de canonicidad](vision/nexus-os-vision-managed-portal.md) sobre cómo se reconcilia.
