# Visión de Nexus OS — Extensión: Portal Gestionado (Hub / Operator / Runtime / Registry)

**Estado:** Aprobado como dirección de arquitectura · **Versión de arquitectura:** `v1alpha1` · **Fecha:** 2026-07-19
**Autor:** Ironbat Digital LLC
**Reconciliado con:** `main` (Console v0.13.8), RFC-002 (Protocolo Console ↔ Platform), catálogo de agentes/áreas, ecosystem registry.

> **Nota sobre canonicidad.** La Visión canónica de Nexus OS (`01_Nexus_OS_Vision.md` / `docs/vision.md`)
> vive en el repositorio `ironbat-jarvis` (Nexus Platform). Este documento es la **extensión oficial
> de esa visión** para la capa de portal gestionado, escrita dentro del repositorio `nexus-console`
> porque es aquí donde se preparan los contratos y esquemas. **No duplica** la visión completa: la
> extiende e indica qué texto de la visión canónica queda **superado** (ver §6). Un PR compañero debe
> incorporar este delta en la visión canónica de `ironbat-jarvis`.

---

## 1. Propósito de esta extensión

La visión original define dos planos: **Nexus Console** (plano de control, este repo) y **Nexus
Platform** (plano de datos, `ironbat-jarvis`). Esta extensión formaliza la evolución **aprobada**
hacia un **portal web gestionado** de cuatro partes, preservando todos los principios existentes
(soberanía del dato, aislamiento fuerte instancia/espacio, agnosticismo de modelo, áreas, Jarvis,
memoria, operación self-hosted).

La propuesta estratégica completa que da origen a esta extensión es
[`NexusOS_Arquitectura_Portal_Gestionado.md`](../architecture/managed-platform-architecture.md#origen)
(reproducida y desarrollada como especificación en `docs/architecture/`).

## 2. Estado actual vs. estado objetivo

Esta distinción es **normativa** en todo el conjunto documental: nada de lo etiquetado como
TARGET-STATE existe hoy como código.

| Capa | ESTADO ACTUAL (v0.13.8, implementado) | ESTADO OBJETIVO (`v1alpha1`, diseño aprobado, no implementado) |
|---|---|---|
| Control | **Nexus Console**: wizard de 6 pasos, deployer (Docker/Fly/K8s), instance registry, secret manager por instancia, agent factory, Jarvis-Console. Habla con Platform por HTTP + JWT firmado (RFC-002). | **Nexus Hub**: SaaS multi-cuenta con cuestionario, motor de blueprint, estado de setup, metadatos de flota, catálogo. La parte hospedada de Console migra conceptualmente al Hub. |
| Reconciliación | Console ejecuta comandos privilegiados directamente (`_console/command`). | **Nexus Operator**: agente open-source, **conexión saliente**, reconcilia estado deseado firmado, **sin shell arbitrario**. |
| Datos | **Nexus Platform**: Jarvis, espacios, áreas, agentes, memoria, usuarios. | **NexusOS Runtime/Platform**: mismo plano de datos soberano, renombrado para dejar claro su rol; opera sin Hub. |
| Distribución | `agent_templates/` en el repo + ecosystem registry (integraciones como datos). | **Nexus Registry**: catálogo firmado y versionado de packs (áreas, agentes, flows, sidecars, skulls). |

## 3. La arquitectura de cuatro partes

### 3.1 Nexus Hub (plano de control remoto, hospedado)
Cara pública del sistema gestionado: registro, cuenta, facturación, cuestionario, blueprint, estado
de tareas de setup, metadatos de flota y catálogo. **No contiene** memoria de usuario,
conversaciones de Jarvis ni datos de negocio. Solo metadatos de flota y salud. Ver
[ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md).

### 3.2 Nexus Operator (agente local, saliente, open-source)
Proceso ligero junto a cada instancia. Abre conexión **saliente** hacia el Hub; recibe documentos de
estado deseado **firmados**; los reconcilia (reconciliation loop); instala packs firmados del
Registry; reporta salud. **No ofrece ejecución de shell arbitraria**: solo comandos de capacidad
acotada. Ver [ADR-0004](../adr/0004-operator-enrollment-and-identity.md).

### 3.3 NexusOS Runtime / Platform (plano de datos soberano)
Consolidación de lo que hoy es Nexus Platform. Aquí viven Jarvis, espacios, áreas, agentes,
meetings, memoria y usuarios finales. **Funciona sin Hub** (modo desconectado). El Operator conecta
Runtime con Hub solo cuando el usuario lo decide.

### 3.4 Nexus Registry (distribución de contenido firmado)
Catálogo versionado de packs. Consultable desde el Hub (catálogo curado) o desde un cliente CLI
open-source contra un registro comunitario, sin pasar por el Hub. Ver
[ADR-0006](../adr/0006-nexus-pack-format.md).

```
Usuario ──> Nexus Hub (registro, cuestionario, blueprint, facturación)
                │  (estado deseado firmado, vía conexión saliente del Operator)
                ▼
        Nexus Operator (junto a la instancia)
                │  (aplica cambios acotados, instala packs, reporta salud)
                ▼
     NexusOS Runtime/Platform (Jarvis, áreas, agentes, memoria, usuarios)
                │  (consulta packs firmados)
                ▼
        Nexus Registry (catálogo firmado y versionado)
```

## 4. Principios preservados (invariantes)

Esta extensión **no altera** los principios de Nexus OS; los refuerza a nivel de infraestructura:

- **Soberanía del dato (P15):** el Hub nunca recibe datos de negocio ni memoria por defecto.
- **Aislamiento (P5):** aislamiento fuerte por instancia también dentro del Hub multi-tenant; sin BD
  compartida de contenido.
- **Auditoría (P12):** toda orden aplicada queda en un log auditable en Hub **y** en la instancia.
- **Reversibilidad (P13):** blueprints versionados, packs con rollback obligatorio, migración opt-in.
- **Agnosticismo de modelo:** el blueprint elige proveedores por instancia; nada se fuerza.
- **Modularidad (P2):** aplicada a la propia infraestructura (dividir Console en Hub + Operator/Admin API).
- **Operación self-hosted:** `docker compose up` sigue existiendo intacto; el Operator es opcional.

## 5. Tres modalidades de despliegue

| Modalidad | Perfil | Quién gestiona | Operator |
|---|---|---|---|
| **Managed** | Sin conocimientos técnicos, ruta simple | Ironbat aloja y aplica actualizaciones vía Hub/Operator | Obligatorio |
| **BYOC** | Soberanía de infraestructura + orquestación del Hub | Usuario aporta cloud; Operator corre ahí; Hub orquesta | Opcional |
| **Self-Hosted / Offline** | Comunidad, control total | Usuario gestiona todo, incluso sin Hub | Ausente por diseño |

## 6. Texto de la visión que queda superado

Esta extensión **supera** (no borra, marca como histórico) cualquier redacción previa que afirme que
**"Console es el único plano de control posible"** o que **"toda gestión remota pasa por Console
ejecutando comandos"**. A partir de `v1alpha1`:

- El plano de control hospedado es **Nexus Hub**; Console es su ancestro directo y su código de wizard
  es base reutilizable (ver [migración](../architecture/migration-and-compatibility.md)).
- La ejecución de cambios sobre la instancia es responsabilidad del **Operator/Runtime Admin API**,
  mediante **comandos declarativos, acotados, firmados y auditables**, nunca shell remoto.
- El modelo "un operador técnico corre comandos Fly" queda superado por "el usuario responde un
  cuestionario y el Operator reconcilia estado deseado".

El protocolo de RFC-002 (Console ↔ Platform por HTTP + JWT firmado) es el **antecedente directo** del
canal Hub ↔ Operator y se generaliza en [ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md).

## 7. Terminología

La terminología formal (Hub, Operator, Runtime, Registry, Instance, Blueprint, SetupPlan, SetupTask,
Area, Agent, Skull/Agent Cognition Profile, Sidecar, Flow, Pack, Overlay, Desired State, Installation)
se define en el [glosario](../architecture/glossary.md). Se mantiene **"Skull"** como alias de marca y
**"Agent Cognition Profile"** como término técnico formal.

## 8. Decisiones abiertas que dependen de negocio/legal

- **Licencia OSS del Runtime/Operator** (Apache-2.0 vs AGPL + dual): pendiente de decisión legal
  formal. Ver [ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md) y
  [frontera OSS/comercial](../architecture/product-oss-boundary.md).
- **Proveedor de firma** (sigstore/cosign vs age envelopes): a resolver en
  [ADR-0002](../adr/0002-signing-and-verification.md).

## 9. Próximos pasos

Este documento y las ADR asociadas son el paso previo a cualquier código de Hub/Operator/Registry. El
roadmap por prioridad (P0–P3), no-goals y criterios de aceptación del MVP están en la
[especificación de arquitectura del portal gestionado](../architecture/managed-platform-architecture.md#roadmap).
