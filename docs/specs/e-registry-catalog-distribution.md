# Spec E: Registry / Catálogo y distribución

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2` (extiende `v1alpha1`)
- **Fecha:** 2026-07-19
- **Contratos:** [`package-access-policy.schema.json`](../schemas/v1alpha2/package-access-policy.schema.json), [`package-download-grant.schema.json`](../schemas/v1alpha2/package-download-grant.schema.json), [`nexus.pack.schema.json`](../schemas/v1alpha1/nexus.pack.schema.json)
- **Relacionadas:** [ADR-0006](../adr/0006-nexus-pack-format.md), [Spec F](f-package-artifact-model.md), [Spec I](i-studio-authoring-publishing.md)

## 1. Problema y contexto

La distribución de packs debe soportar cuatro carriles con garantías distintas: los abiertos deben ser
replicables sin cuenta y de descarga directa; los premium/privados deben protegerse con metadatos
firmados y grants de vida corta, **sin DRM**.

## 2. Objetivos

- Definir carriles `public / community / verified-premium / private-organization`.
- Garantizar que los abiertos son **mirrorable** y **sin cuenta Hub**.
- Emitir **grants de descarga de vida corta** para los carriles cerrados.

## 3. No-objetivos

- DRM, cifrado anti-copia o restricciones sobre OSS. Precios.

## 4. Actores

- **Publicador** (Ironbat verificado, comunidad, organización), **Registry**, **Hub** (grants),
  **cliente/instalador**, **mirror comunitario**.

## 5. Conceptos y modelo de datos

- **PackageAccessPolicy**: `visibility`, `publisher_verification`, `license`, `mirrorable`,
  `requires_hub_account`, `distribution`, `required_entitlements`.
- Conditionals del esquema: public/community => `mirrorable: true`, `requires_hub_account: false`,
  `direct_download`, `required_entitlements` vacío; verified-premium/private-organization =>
  `short_lived_grant` + `required_entitlements` (min 1).
- **Consumo de `OrganizationId` canónico.** El Registry consume el `org_id` (lowercase-canónico,
  emitido por el Hub) tal cual dentro del segmento `private-organization:<org_id>` de un `PackageScope`;
  no lo reescribe ni cambia su caso. Un id con mayúsculas no valida ([common.defs](../schemas/v1alpha2/common.defs.schema.json)).

## 6. Requisitos funcionales

- **P0:** publicar/consultar carriles abiertos sin cuenta; verificación de firma.
- **P1:** emisión de grants para carriles cerrados; validación de entitlement previo.
- **P2:** matriz de compatibilidad y canales de actualización por pack ([ADR-0007](../adr/0007-update-channels-and-rollout.md)).

## 7. Flujos y transiciones de estado

1. Carril abierto: cliente descarga directo desde Registry o mirror; verifica firma; instala.
2. Carril cerrado: cliente presenta entitlement; el Hub emite `PackageDownloadGrant` de vida corta;
   cliente descarga dentro de `max_uses`/`expires_at`; verifica firma; instala.

## 8. Fronteras de API/contrato

- Produce/consume `package-access-policy` y `package-download-grant`. Los packs siguen `nexus.pack`
  (`v1alpha1`), extendido con `visibility` y `required_entitlements` de forma aditiva.

## 9. Seguridad y privacidad

- Firma Cosign (público) / minisign (offline). Grants firmados Ed25519 con `trust_domain`. Sin secretos
  persistentes en el grant.

## 10. Comportamiento ante fallo/offline

- Carriles abiertos replicables para uso air-gapped. Los cerrados requieren un grant vigente; fuera de
  línea se usan artefactos ya descargados.

## 11. Telemetría/observabilidad

- Auditoría de emisión de grants; métricas de catálogo (sin datos de usuario).

## 12. Criterios de aceptación (Given/When/Then)

- **Given** un pack public, **when** se declara con `mirrorable: false`, **then** el contrato lo rechaza.
- **Given** un pack verified-premium, **when** no declara `required_entitlements`, **then** el contrato
  lo rechaza.
- **Given** un usuario sin cuenta, **when** replica un pack community, **then** lo logra sin Hub.

## 13. Métricas de éxito

- 100% de carriles abiertos replicables sin cuenta. Grants siempre de vida corta. Cero DRM.

## 14. Dependencias

- [Spec F](f-package-artifact-model.md), [Spec H](h-security-trust-signing-secrets.md), [Spec B](b-nexus-hub.md).

## 15. Migración/versionado

- Los packs `v1alpha1` sin `visibility` se tratan como públicos (backward compatible).

## 16. Preguntas abiertas

- Política de retención de mirrors; ventana por defecto de `max_uses`/`expires_at` del grant.
