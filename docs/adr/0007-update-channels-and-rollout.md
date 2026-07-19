# ADR-0007: Canales de actualización de runtime/contenido, despliegue escalonado, aprobación y rollback

- **Estado:** Aceptada (política `v1alpha1`)
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0006](0006-nexus-pack-format.md), [ADR-0009](0009-editions-entitlements-and-subscription-degradation.md); esquemas [`desired-state`](../schemas/v1alpha1/desired-state.schema.json), [`nexus.pack`](../schemas/v1alpha1/nexus.pack.schema.json)
- **Revisión `v1alpha2` (2026-07-19):** ver §Extensión `v1alpha2` al final.

## Contexto

Hay dos ciclos de release distintos que no deben acoplarse: el **núcleo** (Runtime/Operator) y el
**contenido** (packs del Registry). Cada instancia puede tener un stack diferente, así que las
actualizaciones deben ser controlables por instancia sin romper packs ya instalados y sin que el Hub
imponga cambios críticos sin consentimiento (soberanía aplicada a la infraestructura).

## Decisión

- **Dos ciclos independientes:** releases del núcleo y releases de contenido, cada uno con su propio
  versionado y canal.
- **Canales por instancia y por pack:** `stable | beta | pinned` (`common.defs#/$defs/UpdateChannel`),
  elegibles de forma independiente para el núcleo y para **cada** pack.
- **Matriz de compatibilidad pública:** qué versión de pack requiere qué versión mínima de Runtime;
  una actualización de núcleo no rompe packs sin aviso.
- **Ciclo de vida de pack:** explorar → previsualizar (diff + coste incremental) → instalar (staging
  local, verificación de firma) → validar (`tests` del manifiesto) → activar → rollback si falla.
- **Despliegue escalonado (staged rollout):** en instancias grandes/organizaciones, una actualización
  puede aplicarse primero a un subconjunto de usuarios o espacios antes de generalizarse.
- **Aprobación obligatoria del `superadmin`** para cambios críticos, **incluso en canal `stable`**:
  el estado deseado marca `requires_superadmin_approval: true` y la tarea queda en `waiting_user`
  hasta aprobación. **Criterio de "crítico"** (decisión #12 de la propuesta): cualquier cambio con
  **migración de datos irreversible** o **cambio de contrato de API pública**.
- **Rollback:** siempre disponible vía el procedimiento `uninstall`/rollback declarado en el manifiesto.

## Consecuencias

- El propietario de la instancia mantiene el control sobre su sistema; las mejoras centrales llegan sin
  imponerse.
- Coste: mantener matriz de compatibilidad y orquestación de staged rollout.

## Alternativas consideradas

- **Auto-actualización de todo en `stable`:** rechazada para cambios críticos; viola soberanía.
- **Un solo canal para núcleo y contenido:** rechazada; acopla ciclos de release distintos.

## Extensión `v1alpha2` (políticas de organización y estado de suscripción)

- La cadencia de actualización pasa a ser un **efecto gobernado por el estado de suscripción**
  (`subscription-state.schema.json#/spec/effects/updates`: `automatic | security_only | manual`). Al
  degradar (suspended/cancelled/expired) las actualizaciones no automáticas siguen disponibles de forma
  manual; **nunca** se fuerza una actualización crítica sin aprobación de superadmin.
- Las organizaciones pueden fijar `team_policy` y `requires_capabilities` en
  `organization-policy.schema.json` (`v1alpha2`), incluyendo canal por rol y por pack. Los roles
  (`owner/admin/member/readonly/guest`) determinan quién aprueba rollouts. Ver
  [Spec C](../specs/c-team-organization.md) y [Spec G](../specs/g-entitlements-subscriptions-degradation.md).
- El staged rollout y la aprobación de cambios críticos se mantienen intactos y aplican por edición.
