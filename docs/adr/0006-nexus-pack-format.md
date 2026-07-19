# ADR-0006: Formato `nexus.pack.yaml`, compatibilidad, dependencias, permisos, tests, SBOM, install/rollback y overlays

- **Estado:** Aceptada (contrato `v1alpha1`)
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0002](0002-signing-and-verification.md), [ADR-0007](0007-update-channels-and-rollout.md); esquema [`nexus.pack`](../schemas/v1alpha1/nexus.pack.schema.json); `console/agent_templates/_schema.md`

## Contexto

Todo lo distribuible vía Registry (áreas, agentes, packs verticales, flows, sidecars, skulls) necesita
un manifiesto único, firmado y versionado. Ya existe un contrato de frontmatter para las plantillas de
agente (`agent_templates/_schema.md`) con `artifact_type` = `agent | sidecar | skill`; el pack debe
componer esas primitivas, no reinventarlas.

## Decisión

- **`nexus.pack.yaml`** (`kind: Pack`) con `version` **inmutable** (SemVer), `publisher` + `signature`,
  `verification` (`verified`/`community`), `license`.
- **Compatibilidad núcleo-paquete:** `spec.compatibility.runtime` (rango SemVer) y `operator` opcional.
  Se mantiene una **matriz de compatibilidad** pública (ver [ADR-0007](0007-update-channels-and-rollout.md)).
- **`dependencies`, `permissions` (con `reason`), `resources`.**
- **Componentes:** `areas`, `agents` (con `artifact_type` alineado a `_schema.md`), `flows`,
  `sidecars`, `skulls` (Agent Cognition Profiles con `model_policy` y `eval_suite`).
- **`tests`** obligatorios (mínimo 1): suite que el pack debe pasar contra la instancia real antes de
  activarse.
- **`uninstall`/rollback** obligatorio (`strategy`): no opcional.
- **`sbom`** (CycloneDX/SPDX) y `license` para trazabilidad legal.
- **Regla de diseño:** un pack **compone primitivas existentes del Runtime**; si necesita su propio
  motor de ejecución distinto, es señal de diseño equivocado y se rechaza en verificación.
- **Overlays:** las personalizaciones locales se aplican como **overlays** (capa encima del pack, sin
  editar sus archivos originales), de forma que una actualización no destruye la personalización
  (equivalente a `values.yaml` sobre un chart de Helm o overlays de Kustomize).

## Consecuencias

- Distribución segura, versionada y verificable; personalización sin fork destructivo.
- Coste: exigir SBOM, firma y suite de tests eleva la barra de publicación (deseable).

## Alternativas consideradas

- **Pack como runtime autónomo:** rechazada; rompe "toda instancia corre el mismo núcleo".
- **Editar el pack in situ para personalizar:** rechazada; los overlays lo sustituyen.
