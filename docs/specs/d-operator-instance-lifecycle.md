# Spec D: Operator y ciclo de vida de instancia

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2` (extiende `v1alpha1`)
- **Fecha:** 2026-07-19
- **Contratos:** [`enrollment.request`](../schemas/v1alpha1/enrollment.request.schema.json), [`enrollment.response`](../schemas/v1alpha1/enrollment.response.schema.json), [`desired-state`](../schemas/v1alpha1/desired-state.schema.json), [`status-report`](../schemas/v1alpha1/status-report.schema.json), [`deployment-modality.schema.json`](../schemas/v1alpha2/deployment-modality.schema.json)
- **Relacionadas:** [ADR-0004](../adr/0004-operator-enrollment-and-identity.md), [Spec J](j-deployment-modalities.md)

## 1. Problema y contexto

El Operator conecta una instancia con el Hub mediante conexión saliente y reconcilia estado deseado
firmado, sin shell arbitrario. En `v1alpha2` además aplica los **efectos de suscripción** y consume
**entitlements** para habilitar capacidades.

## 2. Objetivos

- Enrolamiento seguro (token de un solo uso, par de claves propio, mTLS).
- Reconciliación de estado deseado firmado y de `SubscriptionState`.
- Aplicación de la degradación graciosa sin eliminar datos.

## 3. No-objetivos

- Shell remoto o ejecución arbitraria. Custodia de datos en el Hub.

## 4. Actores

- **Operator**, **Hub**, **Runtime local**, **propietario/admin**.

## 5. Conceptos y modelo de datos

- **Enrollment request/response** (`v1alpha1`). **DesiredState** firmado Ed25519. **SubscriptionState**
  y **Entitlement** (`v1alpha2`). **DeploymentModality** declara `operator: required/optional/absent`.

## 6. Requisitos funcionales

- **P0:** enrolamiento; reconciliación de estado deseado; reporte de salud.
- **P1:** aplicación de efectos de `SubscriptionState` (pausa/reactivación, solo lectura).
- **P2:** staged rollout y aprobación de superadmin para cambios críticos ([ADR-0007](../adr/0007-update-channels-and-rollout.md)).

## 7. Flujos y transiciones de estado

1. `absent` (Personal self-hosted) => sin Operator.
2. `optional` (BYOC) => enrolamiento opt-in; kill switch disponible.
3. `required` (managed) => Operator obligatorio; reconcilia estado deseado y suscripción.
4. Ciclo: enrolar -> reconciliar -> reportar salud -> aplicar efectos -> (rollback si falla).

## 8. Fronteras de API/contrato

- Consume `enrollment.*`, `desired-state`, `entitlement`, `subscription-state`. Produce `status-report`.
  Nunca ejecuta comandos fuera del conjunto acotado.

## 9. Seguridad y privacidad

- Identidad mTLS por instancia distinta de la clave de firma del Hub. Verificación offline de firmas y
  entitlements. Ningún dato de negocio sale de la instancia.

## 10. Comportamiento ante fallo/offline

- Sin Hub, opera con el último estado deseado y entitlement cacheado dentro de la gracia. Kill switch
  desconecta y la instancia sigue autónoma.

## 11. Telemetría/observabilidad

- `status-report` con salud y metadatos; auditoría local de cada intent aplicado.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** modalidad `managed`, **when** se declara sin Operator, **then** el contrato de modalidad la
  rechaza (`operator` debe ser `required`).
- **Given** un estado deseado firmado, **when** el Operator reconcilia, **then** aplica solo intents
  acotados y audita el resultado.
- **Given** un `SubscriptionState` expirado, **when** el Operator lo aplica, **then** pausa agentes
  premium y tareas, sin eliminarlos.

## 13. Métricas de éxito

- Cero shells arbitrarios ejecutados. Reconciliación idempotente. Reactivación completa al renovar.

## 14. Dependencias

- [Spec B](b-nexus-hub.md), [Spec G](g-entitlements-subscriptions-degradation.md), [Spec J](j-deployment-modalities.md).

## 15. Migración/versionado

- Reutiliza contratos `v1alpha1` de enrolamiento/estado deseado; añade consumo de `v1alpha2`.

## 16. Preguntas abiertas

- Formato de canal de transporte definitivo; cadencia de reporte de salud por modalidad.
