# Spec G: Entitlements, suscripciones y degradación graciosa

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`entitlement.schema.json`](../schemas/v1alpha2/entitlement.schema.json), [`subscription-state.schema.json`](../schemas/v1alpha2/subscription-state.schema.json), [`edition.declaration.schema.json`](../schemas/v1alpha2/edition.declaration.schema.json)
- **Relacionadas:** [ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md), [ADR-0002](../adr/0002-signing-and-verification.md)

## 1. Problema y contexto

Las suscripciones deben representarse como capacidades verificables localmente, con expiración y gracia,
y **nunca** deben retener los datos del usuario como rehén al expirar.

## 2. Objetivos

- Verificación **offline** de entitlements con Ed25519 y clave pineada por `trust_domain`.
- Ciclo de vida de suscripción con **degradación graciosa** y sin eliminación de datos.
- Protección anti-replay (`nonce`, `revision`) y expiración (`expires_at`).

## 3. No-objetivos

- Verificación online obligatoria. Precios/planes. Eliminación de datos.

## 4. Actores

- **Hub** (emisor/firmante), **Operator/Runtime** (verificador y aplicador), **propietario**.

## 5. Conceptos y modelo de datos

- **Entitlement**: `metadata` (instance_id, edition, issued_at, expires_at, revision, nonce),
  `spec` (capabilities, package_scopes, seats, offline_verification), `signature` (solo ed25519 +
  trust_domain).
- **SubscriptionState**: `owner_access: preserved` (const), `export_available: true` (const),
  `effects` (additional_users, premium_agents, scheduled_tasks, new_invitations, updates).
- **Invariantes por estado (conditionals del esquema):**
  - active/past_due/grace => additional_users `normal`, premium_agents `running`, scheduled_tasks `running`.
  - suspended/cancelled/expired => additional_users `read_only`, premium_agents `paused`,
    scheduled_tasks `paused`, new_invitations `blocked`.

## 6. Requisitos funcionales

- **P0:** verificar entitlement offline; emitir `EditionDeclaration` derivada; aplicar
  `SubscriptionState`.
- **P1:** ventana de gracia (0-90 días) con entitlement cacheado; revocación por `revision`.
- **P2:** avisos no bloqueantes de renovación (`notice`).

## 7. Flujos y transiciones de estado

```
active --(impago)--> past_due --(fin de plazo)--> grace --(fin de gracia)--> expired
   ^                                                                            |
   +----------------------------- (renovación) --------------------------------+
```

En expired/suspended/cancelled se aplican los efectos de degradación; **el propietario mantiene acceso y
exportación en todos los estados**.

## 8. Fronteras de API/contrato

- Consume `entitlement`, produce `edition.declaration` y `subscription-state`. La firma se valida, no se
  simula: los tests comprueban forma de sobre e invariantes, no criptografía real de fixtures.

## 9. Seguridad y privacidad

- Ed25519 con `trust_domain`; rechazo explícito de `age`, `sigstore-cosign`, `minisign`, `ecdsa-p256`
  como algoritmo de firma de entitlement. `nonce` anti-replay obligatorio.

## 10. Comportamiento ante fallo/offline

- Sin Hub, se usa el entitlement cacheado hasta el fin de la gracia; después, degradación graciosa. La
  edición Personal nunca depende de esto.

## 11. Telemetría/observabilidad

- Auditoría de verificación y de transiciones de estado; sin datos de negocio.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** un entitlement con `algorithm: sigstore-cosign`, **when** se valida, **then** se rechaza.
- **Given** un entitlement sin `metadata.nonce`, **when** se valida, **then** se rechaza.
- **Given** un `SubscriptionState` expired con `owner_access: revoked`, **when** se valida, **then** se
  rechaza (owner debe preservarse).
- **Given** un `SubscriptionState` expired con `premium_agents: running`, **when** se valida, **then** se
  rechaza (debe pausar).

## 13. Métricas de éxito

- Cero pérdida de acceso/exportación del owner. 100% de verificación offline. Reactivación completa al
  renovar.

## 14. Dependencias

- [Spec B](b-nexus-hub.md), [Spec D](d-operator-instance-lifecycle.md), [Spec H](h-security-trust-signing-secrets.md).

## 15. Migración/versionado

- Reutiliza crypto `v1alpha1` por `$id` absoluto; añade contratos de producto `v1alpha2`.

## 16. Preguntas abiertas

- Valor por defecto de la gracia; política de rotación de `revision`; formato del `notice`.
