# Esquemas del Portal Gestionado (`v1alpha1`) y producto Personal + Hub (`v1alpha2`)

Esquemas **JSON Schema 2020-12** que definen los contratos machine-readable del portal gestionado de
NexusOS. **TARGET-STATE:** ningún componente que los consume (Hub, Operator, Registry) está
implementado; estos esquemas fijan la forma acordada **antes** de escribir código.

## Versionado

- Directorios de versión: [`v1alpha1/`](v1alpha1/) (infraestructura) y [`v1alpha2/`](v1alpha2/) (capa de
  producto: ediciones, entitlements, suscripción, acceso a paquetes, modalidades). `v1alpha2` es
  **aditiva**: reutiliza primitivas crypto/identificador de `v1alpha1` por `$id` absoluto y no las rompe.
- Cada esquema lleva `x-nexus-contract-version` (`"v1alpha1"` o `"v1alpha2"`) y un `$id` estable bajo
  `https://schemas.nexusos.dev/<versión>/`.
- La versión de contrato es **independiente** de la versión del paquete `nexus-console`
  (ver [nota de versionado](../architecture/migration-and-compatibility.md#versionado)).
- Convención de estilo: envoltorio `apiVersion: nexus.io/v1alpha1`, `kind`, `metadata`, `spec`
  (coherente con el `nexus.instance.yaml` que emite el wizard actual). `additionalProperties: false`
  donde la forma es cerrada; `enum`/`pattern`/`minimum` donde aplica; `$id`, `title` y `description`
  en todos.

## Esquemas

| Esquema | Contrato | Notas |
|---|---|---|
| [`common.defs.schema.json`](v1alpha1/common.defs.schema.json) | Definiciones compartidas | `SemVer`, `Slug`, `InstanceId`, `Signature` (ed25519/ecdsa/sigstore-cosign/minisign; **age no firma**), `TransparencyLogEntry`, `AgeRecipient`, `SpdxLicense`, `ReplayGuard` |
| [`nexus.blueprint.schema.json`](v1alpha1/nexus.blueprint.schema.json) | `nexus.blueprint.yaml` | Arquitectura recomendada, versionada; sin secretos |
| [`setup.plan.schema.json`](v1alpha1/setup.plan.schema.json) | `setup.plan.yaml` | Plan ordenado de tareas |
| [`setup.task.schema.json`](v1alpha1/setup.task.schema.json) | `SetupTask` | Máquina de estados; `failure_reason` obligatorio si `failed` |
| [`nexus.pack.schema.json`](v1alpha1/nexus.pack.schema.json) | `nexus.pack.yaml` | Firma Sigstore/Cosign + `offline_signature` minisign/Ed25519 + `provenance`; **`license` SPDX obligatoria** y `trademark` separado; `tests` y `uninstall` obligatorios |
| [`desired-state.schema.json`](v1alpha1/desired-state.schema.json) | Estado deseado | Firma **Ed25519** (con `trust_domain` obligatorio; rechaza sigstore/age) + replay guard; intents acotados, sin shell |
| [`enrollment.request.schema.json`](v1alpha1/enrollment.request.schema.json) | Enrolamiento (petición) | Token de un solo uso + clave pública de instancia |
| [`enrollment.response.schema.json`](v1alpha1/enrollment.response.schema.json) | Enrolamiento (respuesta) | Credencial mTLS de vida corta + clave Ed25519 del Hub (no keyless) |
| [`status-report.schema.json`](v1alpha1/status-report.schema.json) | Status/health | Metadatos de flota y salud; nunca contenido |
| [`secrets-bundle-manifest.schema.json`](v1alpha1/secrets-bundle-manifest.schema.json) | Manifiesto público del bundle | **Solo metadatos**; cifrado **age/X25519** (recipiente público); prohíbe valores de secreto por construcción |

## Esquemas `v1alpha2` (producto Personal + Hub)

| Esquema | Contrato | Notas |
|---|---|---|
| [`common.defs.schema.json`](v1alpha2/common.defs.schema.json) | Definiciones de producto | `Edition`, `CapabilityId`, `PackageVisibility`, `PublisherVerification`, `SubscriptionState`, `OrgRole`, `PackageScope`, `GracePeriodDays`, `OfflineVerification` |
| [`edition.declaration.schema.json`](v1alpha2/edition.declaration.schema.json) | `EditionDeclaration` | `source` personal_base/verified_entitlement/cached_entitlement; personal_base implica edición personal |
| [`entitlement.schema.json`](v1alpha2/entitlement.schema.json) | `Entitlement` | Firma **solo Ed25519** + `trust_domain`; `nonce`/`revision`/`expires_at` obligatorios; verificación offline |
| [`subscription-state.schema.json`](v1alpha2/subscription-state.schema.json) | `SubscriptionState` | `owner_access` const preserved, `export_available` const true; efectos pausan (no borran) |
| [`organization-policy.schema.json`](v1alpha2/organization-policy.schema.json) | `OrganizationPolicy` | Membresías (min 1) con rol; `team_policy`; `requires_capabilities` |
| [`package-access-policy.schema.json`](v1alpha2/package-access-policy.schema.json) | `PackageAccessPolicy` | 4 carriles; public/community mirrorable sin cuenta; premium/privado con entitlement + grant |
| [`package-download-grant.schema.json`](v1alpha2/package-download-grant.schema.json) | `PackageDownloadGrant` | Grant de vida corta firmado Ed25519; sin secretos persistentes; no DRM |
| [`deployment-modality.schema.json`](v1alpha2/deployment-modality.schema.json) | `DeploymentModality` | Ortogonal a la edición; rechaza managed+personal |

El [`nexus.pack.schema.json`](v1alpha1/nexus.pack.schema.json) (`v1alpha1`) se extiende de forma
**aditiva** con `metadata.visibility`, `metadata.commercial_terms_ref`, `spec.required_entitlements` y
`publisher.verification: official` (backward compatible).

## Ejemplos (fixtures)

En [`examples/`](examples/), con [`examples/index.json`](examples/index.json) mapeando cada fixture a su
esquema (campo `version` selecciona el directorio, por defecto `v1alpha1`). Cubren `v1alpha1` (Managed
real-estate Madrid/Marbella, BYOC, self-hosted/offline, pack vertical, plan de setup, estado deseado,
enrolamiento, status-report, secrets bundle) y `v1alpha2` (entitlements Personal/Team/gracia, ediciones,
estados de suscripción active/gracia/expirado-degradación, política de organización, cuatro carriles de
paquete, grant de descarga, modalidades Personal self-hosted/Team BYOC/Team managed).

Los **fixtures negativos** viven en [`examples/invalid/`](examples/invalid/) con su propio
[`index.json`](examples/invalid/index.json): cada uno **debe fallar** la validación y así guarda una
invariante (firma no-Ed25519 en entitlement, entitlement sin nonce, suscripción que revoca al owner o
sigue ejecutando al expirar, pack público no replicable, premium sin entitlements, managed+personal).

## Validación

`console/tests/test_managed_platform_schemas.py` valida que (1) cada esquema (ambas versiones) es JSON
Schema 2020-12 válido, (2) cada ejemplo valida contra su esquema (resolviendo `$ref` cross-version por
`$id`), (3) cada fixture negativo es rechazado, (4) ningún ejemplo filtra secretos en texto plano, (5) se
cumplen la forma del sobre de firma e invariantes críticas de producto (edición/entitlement/suscripción/
acceso a paquetes/modalidad) y (6) los enlaces relativos de la documentación resuelven. Se ejecuta con el
`pytest` existente:

```bash
pip install -e "./console[dev]"
cd console && pytest tests/test_managed_platform_schemas.py -q
```
