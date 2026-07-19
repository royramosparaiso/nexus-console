# Changelog de documentación y contratos de NexusOS

Registra cambios en la documentación de arquitectura/producto y en los contratos machine-readable
(`docs/schemas/`). No sigue la versión del paquete `nexus-console` (SemVer del código); los contratos se
versionan por separado (`x-nexus-contract-version`). Formato inspirado en Keep a Changelog.

## [v1alpha2] - 2026-07-19 — Capa de producto Personal + Hub por suscripción

**Estado:** diseño aprobado, no implementado (TARGET-STATE). Aditivo y backward compatible sobre
`v1alpha1`.

### Añadido

- **Visión:** [Personal + Hub por suscripción](vision/nexus-os-vision-personal-hub-subscription.md)
  (ediciones, audiencias, propuesta de valor, fronteras, monetización por capacidad, cuatro carriles de
  paquete, modalidades de despliegue, ciclo de vida ante expiración, promesa OSS, no-objetivos).
- **Especificaciones (a–j):** [`docs/specs/`](specs/README.md) — Personal Runtime, Hub, Team/Org,
  Operator/ciclo de vida, Registry/distribución, modelo de paquetes/artefactos, entitlements/suscripción/
  degradación, seguridad/firma/secretos, Studio y modalidades de despliegue.
- **ADR:** [ADR-0009](adr/0009-editions-entitlements-and-subscription-degradation.md) (ediciones,
  entitlements de capacidad, degradación graciosa) y
  [ADR-0010](adr/0010-edition-vs-deployment-modality.md) (edición ortogonal a modalidad).
- **Esquemas `v1alpha2`** ([`docs/schemas/v1alpha2/`](schemas/v1alpha2/)): `common.defs`,
  `edition.declaration`, `entitlement`, `subscription-state`, `organization-policy`,
  `package-access-policy`, `package-download-grant`, `deployment-modality`.
- **Fixtures:** 17 ejemplos válidos `v1alpha2` y 7 negativos en [`examples/invalid/`](schemas/examples/invalid/)
  con su índice; `examples/index.json` gana `contract_versions` y el campo `version` por caso.
- **Tests:** `console/tests/test_managed_platform_schemas.py` valida ambas versiones, resuelve `$ref`
  cross-version por `$id`, rechaza los fixtures negativos y comprueba invariantes de producto (firma
  Ed25519, anti-replay, preservación del owner/exportación, pausa-no-borrado, mirrorabilidad pública,
  entitlements premium, managed≠personal).

### Cambiado

- **`nexus.pack.schema.json` (`v1alpha1`)**, extensión **aditiva**: `publisher.verification` añade
  `official`; nuevos opcionales `metadata.visibility`, `metadata.commercial_terms_ref`,
  `spec.required_entitlements`; conditional que exige entitlements para visibilidad premium/privada. Los
  packs y ejemplos existentes siguen validando.
- **ADR revisadas:** 0006 (visibilidad/entitlements de pack), 0007 (cadencia de actualización como efecto
  de suscripción + políticas de organización), 0008 (Team Capability Pack propietario + Entitlement
  Verifier OSS).
- **Índices y guías:** `docs/README.md`, `docs/schemas/README.md`, `docs/architecture/glossary.md`
  (sección `v1alpha2`), `docs/architecture/migration-and-compatibility.md` (transición
  `v1alpha1`→`v1alpha2` y política de downgrade), `docs/architecture/product-oss-boundary.md` (nota de
  producto por capacidad).

### Sin cambios (invariantes preservadas)

- Nada de seguridad, exportación o portabilidad se retira del OSS. La edición Personal es libre y
  gratuita, sin Hub. No se hardcodean precios ni planes. El repositorio mixto **permanece MIT** hasta la
  auditoría legal ([ADR-0008](adr/0008-oss-commercial-boundary-and-license.md)).

## [v1alpha1] - 2026-07-19 — Portal Gestionado (línea base)

- Arquitectura de cuatro partes (Hub/Operator/Runtime/Registry), ADR-0001..0008, esquemas `v1alpha1` y
  fixtures. Ver [Visión del Portal Gestionado](vision/nexus-os-vision-managed-portal.md).
