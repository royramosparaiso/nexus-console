# Spec F: Modelo de paquetes y artefactos

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2` (extiende `v1alpha1`)
- **Fecha:** 2026-07-19
- **Contratos:** [`nexus.pack.schema.json`](../schemas/v1alpha1/nexus.pack.schema.json), [`package-access-policy.schema.json`](../schemas/v1alpha2/package-access-policy.schema.json)
- **Relacionadas:** [ADR-0006](../adr/0006-nexus-pack-format.md), [Spec E](e-registry-catalog-distribution.md)

## 1. Problema y contexto

Un pack empaqueta cualquier combinación de artefactos del Runtime (áreas, agentes, skills, flows,
sidecars, skulls, tareas programadas). En `v1alpha2` el pack gana visibilidad y entitlements sin romper
los packs existentes.

## 2. Objetivos

- Cubrir todos los tipos de artefacto como contenido de pack.
- Ligar la visibilidad premium/privada a `required_entitlements` de forma aditiva.
- Mantener el pack como unidad atómica, versionada y firmada.

## 3. No-objetivos

- Convertir un pack en un runtime nuevo. DRM sobre el contenido.

## 4. Actores

- **Autor de pack**, **verificador/instalador**, **Runtime**.

## 5. Conceptos y modelo de datos

- **nexus.pack** (`v1alpha1`) con extensiones aditivas: `metadata.visibility`,
  `metadata.commercial_terms_ref`, `spec.required_entitlements`, `publisher.verification` ampliado con
  `official`.
- **Tipos de artefacto:** área, agente, skill, flow, sidecar, skull (Agent Cognition Profile), tarea
  programada.
- Conditional del esquema: si `visibility` es verified-premium/private-organization, entonces
  `spec.required_entitlements` es obligatorio con min 1 elemento.

## 6. Requisitos funcionales

- **P0:** empaquetar y verificar cualquier combinación de artefactos; SPDX obligatorio.
- **P1:** visibilidad y entitlements; overlays no destructivos.
- **P2:** matriz de compatibilidad `compatibility.runtime`.

## 7. Flujos y transiciones de estado

1. Autor declara `nexus.pack.yaml` con artefactos, licencia SPDX y (opcional) visibilidad.
2. Firma offline (minisign) y/o Cosign; publica en el carril correspondiente ([Spec E](e-registry-catalog-distribution.md)).
3. Instalación: verificar firma -> validar visibilidad/entitlement -> staging -> activar -> rollback si falla.

## 8. Fronteras de API/contrato

- `nexus.pack` (v1alpha1 extendido) + `package-access-policy` (v1alpha2). Compone primitivas del Runtime.

## 9. Seguridad y privacidad

- Firma obligatoria; skulls **nunca** contienen datos ni secretos. Referencias a secretos por nombre.

## 10. Comportamiento ante fallo/offline

- Packs públicos instalables offline; premium requieren grant/entitlement salvo que ya estén en staging.

## 11. Telemetría/observabilidad

- Registro de instalación (`Installation`), auditoría local de activación/rollback.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** un pack sin `metadata.license`, **when** se valida, **then** el contrato lo rechaza.
- **Given** un pack marcado premium sin `required_entitlements`, **when** se valida, **then** se rechaza.
- **Given** un pack `v1alpha1` sin `visibility`, **when** se valida, **then** sigue siendo válido (público).

## 13. Métricas de éxito

- 100% de packs firmados y con SPDX. Backward compatibility total con packs existentes.

## 14. Dependencias

- [Spec E](e-registry-catalog-distribution.md), [Spec H](h-security-trust-signing-secrets.md), [Spec I](i-studio-authoring-publishing.md).

## 15. Migración/versionado

- Todos los campos nuevos son opcionales; los ejemplos existentes siguen validando.

## 16. Preguntas abiertas

- Set canónico de tipos de artefacto vs alias de marca; política de `commercial_terms_ref`.
