# Spec B: Nexus Hub (plano de control hospedado)

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`entitlement.schema.json`](../schemas/v1alpha2/entitlement.schema.json), [`subscription-state.schema.json`](../schemas/v1alpha2/subscription-state.schema.json), [`package-download-grant.schema.json`](../schemas/v1alpha2/package-download-grant.schema.json)
- **Relacionadas:** [ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md), [ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md), [Spec G](g-entitlements-subscriptions-degradation.md)

## 1. Problema y contexto

Las capacidades oficiales de Team/Organization y los paquetes premium/privados requieren un plano de
control hospedado que emita entitlements firmados, gestione cuentas y sirva el catálogo curado. El Hub
**no** custodia datos de negocio ni memoria (principio de soberanía, [visión managed portal](../vision/nexus-os-vision-managed-portal.md)).

## 2. Objetivos

- Emitir **entitlements firmados** (Ed25519) por capacidad, con expiry/gracia/nonce/revision.
- Publicar el **catálogo curado** y emitir **grants de descarga** de vida corta para carriles
  premium/privados.
- Exponer el **SubscriptionState** declarativo que gobierna la degradación graciosa.

## 3. No-objetivos

- Custodiar memoria, conversaciones ni datos de negocio.
- Precios/facturación reales (fuera de alcance; no se hardcodean planes).
- Shell remoto o control imperativo de instancias (solo estado deseado firmado).

## 4. Actores

- **Cuenta/organización**, **propietario/admin**, **Hub KMS/HSM** (firma), **Operator** (consumidor de
  estado deseado y entitlements), **Registry** (catálogo).

## 5. Conceptos y modelo de datos

- **Entitlement**: capacidades, `package_scopes`, `seats`, `offline_verification`, firma Ed25519 con
  `trust_domain`.
- **SubscriptionState**: estado + efectos de degradación (invariantes en Spec G).
- **PackageDownloadGrant**: grant de vida corta por artefacto (no es un secreto persistente).
- **Identificadores canónicos.** El Hub es el **emisor** de `OrganizationId`/`UserRef` y debe emitirlos
  **lowercase-canónicos** (`^org_[a-z0-9]{4,40}$` / `^usr_[a-z0-9]{4,40}$`), normalizándolos a minúsculas
  antes de firmar entitlements/grants. Así un `org_id` viaja sin cambios dentro de un `PackageScope`
  `private-organization:<org_id>` que el Registry y el Runtime consumen; un id con mayúsculas se rechaza
  por contrato ([common.defs](../schemas/v1alpha2/common.defs.schema.json), [glosario](../architecture/glossary.md#v1alpha2)).

## 6. Requisitos funcionales

- **P0:** emisión y rotación de entitlements firmados; publicación de catálogo; emisión de grants.
- **P1:** revocación por `revision` incremental; ventana de gracia offline configurable (0-90 días).
- **P2:** panel de flota (solo metadatos y salud), auditoría de emisiones.

## 7. Flujos y transiciones de estado

1. La cuenta se suscribe (proceso comercial fuera de alcance) y el Hub emite un entitlement firmado.
2. El Operator obtiene y cachea el entitlement; lo verifica offline.
3. Ante renovación/expiración, el Hub actualiza `SubscriptionState`; el Operator aplica los efectos.
4. Para un pack premium, el Hub emite un `PackageDownloadGrant` de vida corta.

## 8. Fronteras de API/contrato

- Produce `entitlement`, `subscription-state`, `package-download-grant` y `desired-state` (`v1alpha1`).
  Consume reportes de salud del Operator. No expone endpoints imperativos de shell.

## 9. Seguridad y privacidad

- Claves de firma en KMS/HSM; break-glass auditado (ver [ADR-0002](../adr/0002-signing-and-verification.md)).
- El Hub nunca recibe datos de negocio. mTLS por instancia para transporte.

## 10. Comportamiento ante fallo/offline

- Si el Hub no está disponible, las instancias operan con entitlements cacheados dentro de la gracia. La
  edición Personal no depende del Hub en ningún caso.

## 11. Telemetría/observabilidad

- Solo metadatos de flota y salud; auditoría de emisión/revocación de entitlements.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** una cuenta suscrita, **when** el Hub emite un entitlement Team, **then** está firmado Ed25519
  con `trust_domain` y es verificable offline.
- **Given** un pack premium, **when** un usuario con entitlement lo solicita, **then** el Hub emite un
  grant de vida corta, no un artefacto DRM.
- **Given** un Hub caído, **when** el Operator arranca, **then** usa el entitlement cacheado dentro de la
  gracia sin degradar.

## 13. Métricas de éxito

- Cero fugas de datos de negocio al Hub. Latencia de emisión de grant baja. Verificación offline 100%.

## 14. Dependencias

- [Spec D](d-operator-instance-lifecycle.md) (Operator), [Spec E](e-registry-catalog-distribution.md),
  [Spec H](h-security-trust-signing-secrets.md).

## 15. Migración/versionado

- Añade contratos `v1alpha2`; reutiliza `desired-state` y crypto de `v1alpha1` por `$id` absoluto.

## 16. Preguntas abiertas

- Proveedor de KMS/HSM definitivo; política de rotación de `trust_domain`; región de datos por defecto.
