# Visión de NexusOS: Personal + Hub por suscripción

**Estado:** Aprobado como dirección de producto y arquitectura · diseño, no implementado (TARGET-STATE)
**Versión de arquitectura:** `v1alpha2` (capa de producto, aditiva sobre `v1alpha1`)
**Fecha:** 2026-07-19
**Autor:** Ironbat Digital LLC
**Reconciliado con:** [Visión del Portal Gestionado (`v1alpha1`)](nexus-os-vision-managed-portal.md), RFC-002, catálogo de agentes/áreas, ecosystem registry.

> **Nota sobre canonicidad.** La Visión canónica de NexusOS vive en el repositorio `ironbat-jarvis`
> (Nexus Platform). Este documento es la **extensión oficial** de esa visión para la capa de producto
> Personal + Hub, escrita en `nexus-console` porque es aquí donde se preparan contratos y esquemas.
> Extiende (no reemplaza) la [Visión del Portal Gestionado](nexus-os-vision-managed-portal.md): esa
> extensión define la infraestructura de cuatro partes (`v1alpha1`); esta añade encima la capa de
> ediciones, entitlements y suscripción (`v1alpha2`). Un PR compañero debe incorporar este delta a la
> visión canónica de `ironbat-jarvis`.

---

## 1. Propósito

Formalizar el modelo de producto aprobado: **cualquiera puede instalar una edición Personal libre y
gratuita de NexusOS para un único propietario**, y las capacidades oficiales multiusuario, de equipo y
de organización, junto con los paquetes premium y privados, se habilitan mediante una **suscripción al
Nexus Hub**. La suscripción se representa como **entitlements firmados verificables localmente**, no como
control remoto ni DRM. Este documento fija ediciones, audiencias, propuesta de valor, fronteras,
principios de monetización, acceso a paquetes, modalidades de despliegue, ciclo de vida ante expiración,
la promesa OSS y los no-objetivos. Distingue **estado actual** de **estado objetivo** de forma
normativa: nada etiquetado como TARGET-STATE existe hoy como código.

## 2. Estado actual vs. estado objetivo

| Capa | ESTADO ACTUAL (v0.13.8, implementado) | ESTADO OBJETIVO (`v1alpha2`, diseño aprobado, no implementado) |
|---|---|---|
| Edición | No hay concepto de edición; Console configura una instancia. | **Personal / Team / Organization** como eje declarado (`edition.declaration`), ortogonal a la modalidad de despliegue. |
| Habilitación | No hay habilitación por capacidad. | **Entitlements** firmados (Ed25519), verificables offline, basados en capacidad (nunca en nombres de plan ni precios). |
| Ciclo de suscripción | No existe. | **SubscriptionState** declarativo con degradación graciosa: el propietario nunca pierde acceso ni exportación. |
| Acceso a paquetes | Ecosystem registry y `agent_templates/` locales; todo abierto. | Cuatro carriles: **public / community** (OSS, replicable, sin cuenta Hub) y **verified-premium / private-organization** (entitlement + grant de descarga de vida corta). |
| Autoría/publicación | Plantillas en repo. | **Studio**: creación verificada de Ironbat, overlays locales del usuario, publicación comunitaria y privada de organización. |

## 3. Ediciones y audiencias

| Edición | Para quién | Capacidades típicas (cualitativo) | Requiere Hub |
|---|---|---|---|
| **Personal** | Cualquier individuo, comunidad, self-hosted | Un único propietario/usuario. Runtime completo, áreas, agentes, memoria, packs public/community, verificación de firmas, exportación total. | No |
| **Team** | Equipos pequeños y profesionales | Multiusuario, roles, colaboración, packs premium, actualizaciones de flota. | Sí (suscripción) |
| **Organization** | Organizaciones y verticales | Todo lo de Team más políticas de organización, packs privados de organización, gobernanza avanzada. | Sí (suscripción) |

La edición es un **eje declarado** (`edition.declaration.schema.json`). Su origen puede ser
`personal_base` (base libre, sin Hub), `verified_entitlement` (entitlement firmado vigente) o
`cached_entitlement` (entitlement en ventana de gracia offline). La edición Personal no requiere ni
entitlement ni conexión.

## 4. Propuesta de valor y foso (moat)

El foso de Ironbat es **conveniencia, curaduría, actualizaciones, compatibilidad, operación de flota,
soporte, confianza y efectos de red**, no el DRM ni restricciones anti-fork. El forking del OSS es
**explícitamente aceptado**: un fork puede reconstruir capacidades libres, pero no obtiene la curaduría
verificada, el catálogo oficial, las actualizaciones coordinadas ni el soporte con SLA. Se cobra por
comodidad operativa y confianza, nunca por soberanía ni seguridad básica.

## 5. Principios de monetización

- **Precios no decididos:** no se fija ninguna cifra ni nombre de plan en código, esquemas ni docs. Los
  entitlements se expresan por **capacidad** (por ejemplo `team_collaboration`, `fleet_management`,
  `premium_pack_access`), nunca por plan comercial.
- **La edición Personal es libre y gratuita indefinidamente.**
- **Nunca se retiene fuera del OSS** nada de seguridad, exportación o portabilidad.
- El coste de los servicios gestionados escala con volumen de uso, número de usuarios y nivel de
  soporte, no con funcionalidades de soberanía.

## 6. Acceso a paquetes (cuatro carriles)

| Carril | Cuenta Hub | Replicable (mirror) | Distribución | Entitlement |
|---|---|---|---|---|
| **public** | No | Sí | Descarga directa | No |
| **community** | No | Sí | Descarga directa | No |
| **verified-premium** | Sí | No | Grant de vida corta | Sí (>=1) |
| **private-organization** | Sí | No | Grant de vida corta | Sí (>=1) |

Los paquetes public y community son **OSS, replicables sin cuenta Hub y de descarga directa**. Los
premium y privados usan **metadatos firmados + grants de descarga de vida corta** (`package-download-grant`),
**nunca DRM**. Un fork puede replicar libremente los carriles abiertos.

## 7. Modalidades de despliegue (ortogonales a la edición)

La **modalidad** (`self_hosted` / `byoc` / `managed`) es **independiente** de la edición
(`deployment-modality.schema.json`). Personal puede ser self-hosted; Team puede ser BYOC o managed. La
**única** combinación rechazada por contrato es **managed + personal**: la operación gestionada por
Ironbat presupone edición Team/Organization. Ver
[ADR-0010](../adr/0010-edition-vs-deployment-modality.md).

## 8. Ciclo de vida ante expiración (degradación graciosa)

**Nunca se retienen los datos como rehén.** En cualquier estado de suscripción
(`subscription-state.schema.json`):

- **El propietario conserva acceso siempre** (`owner_access` fijado a `preserved`).
- **La exportación total está siempre disponible** (`export_available` fijado a `true`).
- Al expirar/suspender/cancelar: los **usuarios adicionales pasan a solo lectura**, los **agentes
  premium y las tareas programadas se PAUSAN (no se eliminan)** y se reactivan al renovar. Las
  **capacidades Personal continúan**.
- **No hay eliminación de datos** en ningún estado. Ver [ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md).

## 9. Verificación de entitlements

Los entitlements son **documentos de capacidad firmados** (`entitlement.schema.json`), verificables
localmente con **Ed25519** y una clave del Hub pineada por `trust_domain`. Incluyen `expires_at`,
ventana de gracia, `nonce` (anti-replay), `revision` y firma. **Personal no requiere ninguna
verificación online.** Team/Organization operan offline dentro de la ventana de gracia usando un
entitlement cacheado.

## 10. Promesa OSS

- Personal es libre y gratuita, para un propietario, sin Hub.
- Agentes, skills, flows, sidecars, skulls, tareas programadas y packs **públicos** siguen siendo OSS y
  usables sin login en el Hub.
- Seguridad, exportación y portabilidad permanecen en OSS en todas las ediciones.
- El forking está aceptado; el valor diferencial es la curaduría y la operación, no la restricción.

## 11. Licencia: estado actual vs objetivo

El modelo de **licencia por componente** está aprobado ([ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md)):
Apache-2.0 (tras auditoría legal) para Runtime, Operator, CLI, SDK, contratos/esquemas e instaladores;
**propietario** para el Hub y el **Team Capability Pack**. El repositorio mixto actual **sigue siendo
MIT** hasta completar la auditoría de titularidad/contribución. **No se afirma que las licencias ya
hayan cambiado.**

## 12. No-objetivos (explícitos)

No se implementan (ni se especifican como existentes): precios de facturación, integración de pago real,
acceso a shell remoto, DRM, eliminación de datos ante expiración, ni restricciones ocultas sobre la
edición Personal OSS. Las capacidades de runtime aquí descritas son **especificación**, no
implementación; la entrega es por fases.

## 13. Terminología y especificaciones

Los términos nuevos (Edition, Entitlement, Capability, SubscriptionState, Package Visibility, Download
Grant, Deployment Modality, Organization Policy) se definen en el
[glosario](../architecture/glossary.md#v1alpha2). Las especificaciones detalladas, listas para
implementar, están en [`docs/specs/`](../specs/README.md).
