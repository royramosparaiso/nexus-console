# Spec A: Personal Runtime (edición Personal)

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`edition.declaration.schema.json`](../schemas/v1alpha2/edition.declaration.schema.json), [`deployment-modality.schema.json`](../schemas/v1alpha2/deployment-modality.schema.json)
- **Relacionadas:** [ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md), [ADR-0010](../adr/0010-edition-vs-deployment-modality.md), [Spec G](g-entitlements-subscriptions-degradation.md)

## 1. Problema y contexto

Cualquier persona debe poder instalar y usar una edición **Personal** libre y gratuita de NexusOS para un
único propietario, sin cuenta en el Hub, sin conexión y sin ningún componente de pago. Hoy Console
configura instancias pero no existe el concepto de edición ni una base libre autónoma garantizada.

## 2. Objetivos

- Ejecutar el Runtime completo (áreas, agentes, memoria, flows) para un propietario sin Hub.
- Instalar y verificar packs de los carriles **public** y **community** sin cuenta.
- Exportar la instancia completa en cualquier momento.
- Declarar la edición de forma verificable (`edition.declaration` con `source: personal_base`).

## 3. No-objetivos

- Multiusuario, roles y colaboración (ver [Spec C](c-team-organization.md)).
- Packs premium/privados (ver [Spec E](e-registry-catalog-distribution.md)).
- Cualquier verificación online obligatoria.

## 4. Actores

- **Propietario** (único usuario de la edición Personal).
- **Runtime local** (plano de datos soberano).
- **CLI/instalador de packs** (OSS).

## 5. Conceptos y modelo de datos

- **EditionDeclaration** (`source: personal_base` implica `edition: personal`; validado por conditional
  en el esquema).
- **Deployment modality** por defecto `self_hosted`, `operator: absent`, `managed_by: owner`.
- Reutiliza primitivas `v1alpha1`: Instance, Area, Agent, Skull, Pack, Overlay.

## 6. Requisitos funcionales

- **P0:** arranque local sin Hub; declaración de edición Personal; instalar packs public/community;
  verificar firmas offline; exportación total.
- **P1:** overlays locales sobre packs; actualización manual de packs desde mirror comunitario.
- **P2:** ruta de upgrade a Team mediante entitlement (sin migrar datos fuera de la instancia).

## 7. Flujos y transiciones de estado

1. Instalación local (`docker compose up` sigue siendo válido).
2. Runtime emite `EditionDeclaration` con `source: personal_base`.
3. El propietario instala packs open; el instalador verifica firma minisign/cosign.
4. Upgrade opcional: al presentar un entitlement Team vigente, `source` pasa a `verified_entitlement`
   sin tocar datos existentes.

## 8. Fronteras de API/contrato

- Emite `edition.declaration` (v1alpha2). No consume Hub. Los packs se resuelven por el contrato
  `nexus.pack` (`v1alpha1`, extendido de forma aditiva).

## 9. Seguridad y privacidad

- Ningún dato sale de la instancia. Verificación de firmas local. Sin telemetría obligatoria.

## 10. Comportamiento ante fallo/offline

- Diseñado para operar **siempre offline**. No hay dependencia de red para ninguna capacidad Personal.

## 11. Telemetría/observabilidad

- Solo local y opt-in. La edición Personal no reporta al Hub.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** un host sin cuenta Hub, **when** el propietario instala NexusOS, **then** obtiene un Runtime
  funcional con `edition: personal` sin conexión.
- **Given** un pack community firmado, **when** se instala offline, **then** la firma se verifica y el
  pack queda activo sin cuenta.
- **Given** una instancia Personal, **when** el propietario solicita exportación, **then** obtiene un
  export completo y portable.

## 13. Métricas de éxito

- 100% de capacidades Personal disponibles sin red. Tiempo de arranque local dentro del presupuesto del
  Runtime. Cero llamadas salientes obligatorias.

## 14. Dependencias

- Runtime `v1alpha1`, contrato de packs, verificador OSS. Ver [Spec H](h-security-trust-signing-secrets.md).

## 15. Migración/versionado

- Aditiva sobre `v1alpha1`. Las instancias v0.13.8 se declaran Personal por defecto. Ver
  [migración](../architecture/migration-and-compatibility.md).

## 16. Preguntas abiertas

- Formato exacto del artefacto de exportación portable (candidato: bundle firmado). Región de datos por
  defecto (no aplica a Personal self-hosted).
