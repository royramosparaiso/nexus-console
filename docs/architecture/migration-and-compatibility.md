# Migración y compatibilidad — de Console/Platform (v0.13.8) al Portal Gestionado

- **Estado:** Diseño aprobado · no implementado
- **Versión de arquitectura:** `v1alpha1`
- **Fecha:** 2026-07-19
- **Relacionadas:** [ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md), [especificación §7](managed-platform-architecture.md#migration), RFC-002

## Principio rector

La migración al portal gestionado es **opt-in, no destructiva, reversible** y permite **operación
standalone indefinida**. Nadie pierde funcionalidad ni queda obligado a conectarse al Hub. Esto es la
aplicación directa del principio de soberanía del dato a la propia infraestructura.

## Qué pasa con cada activo actual

| Activo actual (v0.13.8) | Qué le ocurre | Reversible / standalone |
|---|---|---|
| **Console local** (`docker compose up`) | Sigue funcionando **idéntico**. Modo local single-tenant intacto. El Hub es opcional. | Sí, indefinidamente |
| **`nexus.instance.yaml`** (wizard) | Es base directa del `Blueprint`. Un adaptador puede derivar `nexus.blueprint.yaml` de un `nexus.instance.yaml` existente sin pérdida. | Sí; el instance.yaml sigue siendo válido |
| **Outputs de handoff** (`SETUP.md`, plan de provisioning) | `SETUP.md` se conserva como checklist humano; el plan se formaliza como `setup.plan.yaml`. Los outputs actuales siguen siendo usables tal cual. | Sí |
| **Despliegues Fly.io** existentes | Siguen operando bajo el flujo Console/Fly manual. La adopción del Operator es **opcional**; sin él, nada cambia. | Sí |
| **Platform desplegadas** | Se renombran conceptualmente a **NexusOS Runtime**; el protocolo RFC-002 (HTTP + JWT firmado) sigue vigente y es el antecedente del canal Hub↔Operator. | Sí |
| **Plantillas de agente / áreas** (`console/agent_templates/`) | Se empaquetan como **packs** del Registry sin cambiar su frontmatter (`_schema.md`). Las asignaciones de área (`area_recommender`) se preservan. | Sí; el catálogo local sigue disponible |
| **Ecosystem registry / integraciones** | El modelo de "integraciones como datos" (referencias a secretos por nombre, nunca valores) es coherente con [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md) y se conserva. | Sí |
| **Instancias v0.13.8** | Pueden enrolarse en el Hub instalando el Operator (P1), o seguir sin él. El enrolamiento no toca datos de negocio. | Sí; kill switch disponible |

## Ruta de migración opt-in (cuando exista Operator, P1)

1. El operador instala el **Operator** junto a su instancia (sidecar/systemd/pod).
2. El Hub emite un **token de enrolamiento de un solo uso**; el Operator genera su par de claves e
   intercambia el token ([ADR-0004](../adr/0004-operator-enrollment-and-identity.md)).
3. A partir de ahí, el Operator reconcilia estado deseado firmado. **Ningún dato de negocio migra al
   Hub.**
4. En cualquier momento, el **kill switch** desconecta el Operator; la instancia sigue operando en
   modo autónomo.

## Compatibilidad de versiones

- El **contrato de arquitectura** se versiona como `v1alpha1`, independiente de la versión del paquete
  `nexus-console` (hoy `0.13.8`). Ver [nota de versionado](#versionado).
- Los packs declaran `compatibility.runtime` (rango SemVer); una **matriz de compatibilidad** pública
  evita romper packs instalados ([ADR-0007](../adr/0007-update-channels-and-rollout.md)).
- Backward compatibility del protocolo: una versión minor, igual que RFC-002.

## Reversibilidad

- Blueprints versionados (nunca sobrescriben): se puede volver a una versión anterior.
- Packs con `uninstall`/rollback obligatorio y overlays no destructivos.
- Export/portabilidad de la instancia completa disponible en OSS (no se retiene fuera del OSS).

<a id="versionado"></a>
## Nota de versionado

`console/pyproject.toml` está en `0.13.8` y sigue SemVer del paquete. Este trabajo es **solo
documentación y contratos de una arquitectura futura no implementada**, por lo que **no** se bumpea la
versión del paquete: no hay cambio de comportamiento del código. En su lugar, la arquitectura y los
esquemas se versionan por separado como **`v1alpha1`** (`x-nexus-contract-version` en cada esquema),
señalando que es un contrato en fase alfa, sujeto a cambios antes de la implementación. Cuando el
primer componente (P0 del Hub) se implemente, ese código seguirá el versionado SemVer del paquete que
corresponda.
