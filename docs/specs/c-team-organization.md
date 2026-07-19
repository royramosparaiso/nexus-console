# Spec C: Team / Organization (multiusuario y gobernanza)

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`organization-policy.schema.json`](../schemas/v1alpha2/organization-policy.schema.json), [`entitlement.schema.json`](../schemas/v1alpha2/entitlement.schema.json), [`edition.declaration.schema.json`](../schemas/v1alpha2/edition.declaration.schema.json)
- **Relacionadas:** [Spec B](b-nexus-hub.md), [Spec G](g-entitlements-subscriptions-degradation.md)

## 1. Problema y contexto

Las capacidades oficiales multiusuario, de equipo y de organización deben habilitarse por suscripción y
representarse como capacidades verificables, sin acoplarse a nombres de plan ni precios.

## 2. Objetivos

- Modelar membresías y roles (`owner/admin/member/readonly/guest`).
- Habilitar colaboración, invitaciones y políticas por capacidad (`team_collaboration`,
  `fleet_management`, etc.).
- Aplicar políticas de organización sobre packs, roles y actualizaciones.

## 3. No-objetivos

- Facturación/pricing. SSO empresarial concreto (se referencia como capacidad futura, no se especifica
  el proveedor). Datos de negocio en el Hub.

## 4. Actores

- **Organization**, **owner/admin/member/readonly/guest**, **Hub** (emite entitlement + policy),
  **Operator** (aplica).

## 5. Conceptos y modelo de datos

- **OrganizationPolicy**: `memberships` (min 1, `user_ref` + `role`), `team_policy`,
  `requires_capabilities`.
- **Entitlement** con `seats` y capacidades de equipo.
- **EditionDeclaration** con `source: verified_entitlement`.

## 6. Requisitos funcionales

- **P0:** membresías y roles; capacidades de colaboración gated por entitlement.
- **P1:** políticas de organización sobre packs privados y canales de actualización.
- **P2:** gobernanza avanzada (aprobaciones, auditoría por organización).

## 7. Flujos y transiciones de estado

1. La organización se suscribe; el Hub emite entitlement Team/Org + `OrganizationPolicy`.
2. El owner invita usuarios; los roles determinan permisos.
3. Al expirar, los usuarios adicionales pasan a solo lectura (ver [Spec G](g-entitlements-subscriptions-degradation.md)); el owner conserva acceso.

## 8. Fronteras de API/contrato

- Consume `entitlement` y `organization-policy`. Produce cambios de edición vía `edition.declaration`.

## 9. Seguridad y privacidad

- Roles aplicados en el Runtime local; el Hub solo conoce metadatos de membresía, no contenido.

## 10. Comportamiento ante fallo/offline

- Operación offline dentro de la gracia con entitlement cacheado; degradación graciosa al expirar.

## 11. Telemetría/observabilidad

- Auditoría de cambios de membresía y rol; métricas de flota (solo metadatos).

## 12. Criterios de aceptación (Given/When/Then)

- **Given** una org sin entitlement `team_collaboration`, **when** intenta invitar usuarios, **then** la
  capacidad no está disponible.
- **Given** una org con entitlement vigente, **when** define `OrganizationPolicy` con >=1 membresía,
  **then** valida y se aplica.
- **Given** un entitlement expirado, **when** se reevalúa, **then** los usuarios adicionales quedan en
  solo lectura y el owner mantiene acceso.

## 13. Métricas de éxito

- Cero pérdida de acceso del owner en cualquier estado. Aplicación correcta de roles offline.

## 14. Dependencias

- [Spec B](b-nexus-hub.md), [Spec G](g-entitlements-subscriptions-degradation.md).

## 15. Migración/versionado

- Aditiva; las instancias Personal no se ven afectadas.

## 16. Preguntas abiertas

- Catálogo definitivo de capacidades de organización; proveedor SSO; límites de `seats` por defecto.
