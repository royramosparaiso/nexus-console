# Spec J: Modalidades de despliegue (ortogonales a la edición)

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`deployment-modality.schema.json`](../schemas/v1alpha2/deployment-modality.schema.json), [`edition.declaration.schema.json`](../schemas/v1alpha2/edition.declaration.schema.json)
- **Relacionadas:** [ADR-0010](../adr/0010-edition-vs-deployment-modality.md), [Spec D](d-operator-instance-lifecycle.md)

## 1. Problema y contexto

Dónde y cómo se despliega una instancia (self-hosted, BYOC, managed) es **independiente** de qué edición
usa (Personal, Team, Organization). Acoplarlas confundiría soberanía con capacidad de producto.

## 2. Objetivos

- Modelar la modalidad como eje separado de la edición.
- Permitir todas las combinaciones razonables (Personal self-hosted, Team BYOC, Team managed, etc.).
- Rechazar por contrato la única combinación inválida: **managed + personal**.

## 3. No-objetivos

- Forzar managed para ninguna edición. Acoplar precio a modalidad.

## 4. Actores

- **Propietario/organización**, **Ironbat** (solo en managed), **Operator**.

## 5. Conceptos y modelo de datos

- **DeploymentModality**: `modality` (self_hosted/byoc/managed), `edition`, `operator`
  (required/optional/absent), `managed_by` (owner/ironbat), `data_region`.
- **Conditionals del esquema:**
  - `managed` => `operator: required`, `managed_by: ironbat`, `edition` en {team, organization}
    (rechaza personal).
  - `self_hosted` => `operator: absent`, `managed_by: owner`.
  - `byoc` => `managed_by: owner`.

## 6. Requisitos funcionales

- **P0:** declarar modalidad y validar la ortogonalidad.
- **P1:** transiciones de modalidad (self-hosted -> BYOC -> managed) sin cambiar edición.
- **P2:** región de datos por modalidad managed.

## 7. Flujos y transiciones de estado

1. Personal self-hosted: sin Operator, gestionado por el owner.
2. Team BYOC: Operator opcional; el owner aporta cloud.
3. Team managed: Operator obligatorio; Ironbat aloja.
4. Cambiar de modalidad no altera la edición ni los datos.

## 8. Fronteras de API/contrato

- Produce `deployment-modality`. Coherente con `edition.declaration` (ejes separados).

## 9. Seguridad y privacidad

- Managed implica que Ironbat opera infraestructura, nunca que accede a datos de negocio (sigue soberanía
  y mTLS por instancia).

## 10. Comportamiento ante fallo/offline

- self_hosted y byoc operan sin Hub; managed requiere Operator pero conserva gracia offline.

## 11. Telemetría/observabilidad

- Metadatos de modalidad y salud; sin datos de negocio.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** `modality: managed` + `edition: personal`, **when** se valida, **then** se rechaza.
- **Given** `modality: self_hosted`, **when** declara `operator: required`, **then** se rechaza (debe ser
  absent).
- **Given** `modality: byoc` + `edition: team`, **when** se valida, **then** valida correctamente.

## 13. Métricas de éxito

- Todas las combinaciones válidas aceptadas; solo managed+personal rechazada. Cambios de modalidad sin
  pérdida de datos.

## 14. Dependencias

- [Spec D](d-operator-instance-lifecycle.md), [Spec A](a-personal-runtime.md), [Spec C](c-team-organization.md).

## 15. Migración/versionado

- Aditiva; las instancias existentes se declaran self_hosted por defecto.

## 16. Preguntas abiertas

- Catálogo de regiones de datos; si BYOC managed (híbrido) merece una cuarta modalidad futura.
