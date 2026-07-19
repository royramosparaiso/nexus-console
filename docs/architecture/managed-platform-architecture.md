# Especificación de arquitectura — Portal Gestionado de NexusOS (`v1alpha1`)

- **Estado:** Diseño aprobado · **no implementado** (TARGET-STATE salvo donde se indique ACTUAL)
- **Versión de arquitectura:** `v1alpha1`
- **Fecha:** 2026-07-19
- **Deriva de:** la propuesta estratégica aprobada `NexusOS_Arquitectura_Portal_Gestionado.md`
- **Documentos hermanos:** [Visión: Portal Gestionado](../vision/nexus-os-vision-managed-portal.md), [ADR-0001…0008](../adr/), [glosario](glossary.md), [migración](migration-and-compatibility.md), [frontera OSS/comercial](product-oss-boundary.md)

> <a id="origen"></a>**Origen y alcance.** Este documento desarrolla la propuesta aprobada como
> especificación técnica de referencia. **No** implementa Hub, Operator, Registry, ejecución remota,
> facturación ni provisioning. Ningún componente descrito como TARGET-STATE existe como código.

## Índice

1. [Contexto del sistema y fronteras de confianza](#contexto)
2. [User journeys: Managed, BYOC, Self-Hosted](#journeys)
3. [Máquina de estados de tareas de setup](#state-machine)
4. [Modelo de datos del Hub y frontera de datos solo-Runtime](#data-model)
5. [Contratos de API y eventos representativos](#api)
6. [Ciclo de vida de paquetes y gobernanza del Registry](#packages)
7. [Migración de despliegues Console/Fly actuales](#migration)
8. [Modelo de amenazas y controles](#threat)
9. [Observabilidad y auditoría](#observability)
10. [Modos de fallo, comportamiento offline y recuperación ante desastres](#failure)
11. [Roadmap P0–P3, no-goals, métricas y criterios de aceptación del MVP](#roadmap)

---

<a id="contexto"></a>
## 1. Contexto del sistema y fronteras de confianza

Cuatro componentes con fronteras de confianza explícitas (ver [ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md)):

```
                         Zona de confianza: Ironbat (hospedado)
        ┌───────────────────────────────────────────────────────┐
        │  Nexus Hub  ── cuentas, cuestionario, blueprint,        │
        │               estado de setup, metadatos de flota,      │
        │               catálogo. NO datos de negocio.            │
        └───────▲───────────────────────────────────┬────────────┘
                │ estado deseado firmado             │ catálogo firmado
   status-report│ (saliente, iniciada por Operator)  │
                │                                    ▼
        ┌───────┴────────────┐             ┌──────────────────────┐
        │  Nexus Operator     │            │   Nexus Registry      │
        │  (OSS, sin shell)   │            │ (packs firmados)      │
        └───────┬────────────┘             └──────────────────────┘
                │ Runtime Admin API (local, autenticación fuerte)
                ▼
   Zona de confianza: instancia soberana del usuario
        ┌───────────────────────────────────────────────────────┐
        │  NexusOS Runtime/Platform ── Jarvis, espacios, áreas,   │
        │  agentes, memoria, usuarios, vault local de secretos.   │
        └───────────────────────────────────────────────────────┘
```

**Fronteras de confianza (normativas):**

- **Hub ↔ Operator:** solo el Operator inicia la conexión (saliente). El Hub solo envía **estado
  deseado firmado** y recibe **status-report** (metadatos/salud). Sin canal de shell.
- **Operator ↔ Runtime:** el Operator invoca el **Runtime Admin API** local con capacidades acotadas.
  Nunca ejecuta código arbitrario.
- **Datos de negocio y memoria:** viven **solo** en el Runtime. El Hub no los recibe por defecto.
- **Secretos:** en el vault local del Runtime; el Hub solo maneja el manifiesto público del bundle
  cifrado (ver [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md)).

<a id="journeys"></a>
## 2. User journeys

**Común (registro → operativa):** registro → creación de instancia y elección de modalidad →
cuestionario → generación de blueprint (7 artefactos) → revisión humana (arquitectura, coste,
permisos, riesgos) → aprovisionamiento → tareas de setup → instancia operativa → ciclo de vida
continuo.

### 2.1 Managed
El Hub orquesta el despliegue en infraestructura de Ironbat. El **Operator es obligatorio**. El usuario
solo aprueba pasos y conecta cuentas OAuth cuando se le pide. Ejemplo:
[`blueprint.managed-real-estate.yaml`](../schemas/examples/blueprint.managed-real-estate.yaml).

### 2.2 BYOC (Bring Your Own Cloud)
El usuario conecta su cuenta cloud (Fly/AWS/GCP/on-prem). El Hub genera el plan; el **Operator** se
instala en la infraestructura del usuario y ejecuta el resto. El Operator es **opcional** pero
recomendado. Ejemplo: [`blueprint.byoc.yaml`](../schemas/examples/blueprint.byoc.yaml).

### 2.3 Self-Hosted / Offline
El Hub, si se usa, solo entrega artefactos de handoff (`SETUP.md`, `setup.plan.yaml`). **Sin Operator y
sin conexión al Hub.** La instancia opera indefinidamente en modo autónomo. Ejemplo:
[`blueprint.self-hosted-offline.yaml`](../schemas/examples/blueprint.self-hosted-offline.yaml).

<a id="state-machine"></a>
## 3. Máquina de estados de tareas de setup

Esquema: [`setup.task.schema.json`](../schemas/v1alpha1/setup.task.schema.json). Ver
[ADR-0003](../adr/0003-blueprint-and-setup-plan-contracts.md).

```
not_started ─▶ waiting_user ─▶ waiting_oauth ─▶ ready ─▶ running ─▶ completed
     │              │                │            │         │
     └──────────────┴────────────────┴────────────┴─────────┴──▶ blocked
                                                             ├──▶ failed  (failure_reason obligatorio)
                                                             └──▶ skipped (decisión del usuario)
```

| Estado | Significado |
|---|---|
| `not_started` | Definida, no iniciada |
| `waiting_user` | Requiere acción humana no técnica |
| `waiting_oauth` | Requiere autorización OAuth/conexión externa |
| `ready` | Dependencias resueltas, lista |
| `running` | En ejecución (Operator o cowork) |
| `blocked` | Bloqueada por dependencia/conflicto |
| `completed` | Verificada con evidencia |
| `failed` | Fallida, con `failure_reason` |
| `skipped` | Omitida intencionalmente |

Cada tarea registra `owner` (`hub_automated`/`operator`/`user`/`cowork_assistant`), `prerequisites`,
`evidence` (respuesta de API, hash, healthcheck — nunca el secreto), `retry` (backoff con tope),
`rollback` y `escalation` a soporte. Una tarea bloqueada no detiene el resto si no hay dependencia
directa; el usuario ve siempre el punto exacto de su instancia.

<a id="data-model"></a>
## 4. Modelo de datos del Hub y frontera de datos solo-Runtime

**Ninguna entidad del Hub contiene memoria, conversaciones ni datos de negocio.**

| Entidad | Propósito | Datos de negocio |
|---|---|---|
| `Account` | Cuenta de usuario del Hub | No |
| `Organization` | Agrupación facturable | No |
| `Instance` | Metadatos (nombre, modalidad, región declarada, versión) | No |
| `Blueprint` | Arquitectura recomendada (versionada) | No |
| `SetupPlan` / `SetupTask` | Plan y tareas con estado/ownership/evidencia | No |
| `Enrollment` | Registro de enrolamiento del Operator (claves, token usado) | No |
| `Package` / `PackageVersion` | Definición y versión de pack del Registry | No |
| `Installation` | Qué pack/versión está en qué instancia | No |
| `SecretReference` | Puntero a secreto (no el valor) | No |
| `Deployment` | Despliegue/actualización aplicada | No |
| `HealthSnapshot` | Telemetría de salud agregada | No |
| `AuditEvent` | Evento de auditoría del Hub | No |
| `Subscription` | Plan de facturación | No |
| **Memoria, conversaciones, contenido de áreas** | — | **Solo Runtime** |

Multi-organización soportada en el modelo desde el día uno (`Organization`); la UI de gestión puede
llegar en P1.

<a id="api"></a>
## 5. Contratos de API y eventos representativos

No es un OpenAPI completo; delimita la frontera Hub-Operator-Registry. Todos los endpoints que mutan
estado exigen autenticación con la clave de esa instancia (respuestas del Operator) o sesión de
usuario con rol suficiente (acciones desde el Hub).

**Enrolamiento** — ver [ADR-0004](../adr/0004-operator-enrollment-and-identity.md):
- `POST /v1/instances/{id}/enrollment-token` → token de un solo uso, vida corta.
- `POST /v1/enroll` → intercambia token por par de claves ([`enrollment.request`](../schemas/v1alpha1/enrollment.request.schema.json) → [`enrollment.response`](../schemas/v1alpha1/enrollment.response.schema.json)).

**Estado deseado** — ver [`desired-state`](../schemas/v1alpha1/desired-state.schema.json):
- `GET /v1/instances/{id}/desired-state` (poll) o evento `desired_state.updated` (push WebSocket).

**Reporte de estado** — ver [`status-report`](../schemas/v1alpha1/status-report.schema.json):
- `POST /v1/instances/{id}/status-report`. Evento `instance.health_changed` a dashboards internos.

**Paquetes:**
- `POST /v1/instances/{id}/packages/install` · `POST /v1/instances/{id}/packages/{id}/rollback`.
- Eventos `package.install.completed` / `package.install.failed`.

**Plan de setup:**
- `GET /v1/instances/{id}/setup-plan` · `PATCH /v1/setup-tasks/{id}` (Operator o cowork autorizado).

**Registry:**
- `GET /v1/registry/packages?area=legal&compatibility=runtime>=1.0`.
- `GET /v1/registry/packages/{id}/versions/{version}/manifest` → manifiesto firmado.

<a id="packages"></a>
## 6. Ciclo de vida de paquetes y gobernanza del Registry

Ver [ADR-0006](../adr/0006-nexus-pack-format.md) y [ADR-0007](../adr/0007-update-channels-and-rollout.md).
Explorar → previsualizar (diff + coste incremental) → instalar (staging local + verificación de firma)
→ validar (`tests` del manifiesto) → activar → canales (`stable`/`beta`/`pinned`) → staged rollout →
rollback → fork local (overlay) → publicar de vuelta (opcional).

**Gobernanza:** un solo Registry técnico con campo `verification` (`verified`/`community`) visible en
el catálogo (decisión #7). Firma obligatoria, SBOM y suite de `tests` como barra de publicación.
Packs verticales construidos por Ironbat en el MVP; partners verificados en P2.

<a id="migration"></a>
## 7. Migración de despliegues Console/Fly actuales

Resumen aquí; detalle en [migración y compatibilidad](migration-and-compatibility.md). La migración es
**opt-in, no destructiva, reversible** y permite operación standalone indefinida. Los outputs actuales
del wizard/handoff (`nexus.instance.yaml`, `SETUP.md`) son base directa del blueprint/plan; los
despliegues Fly siguen funcionando sin Operator.

<a id="threat"></a>
## 8. Modelo de amenazas y controles

| Amenaza | Control |
|---|---|
| Shell remoto / ejecución arbitraria | **No existe canal de shell**; solo capacidades acotadas enumeradas en `desired-state` |
| Estado deseado manipulado | Firma **Ed25519** (clave del Hub en KMS/HSM, pineada en el Operator) + canonicalización + verificación **100% offline**, sin dependencia de Sigstore ni de transparency log ([ADR-0002](../adr/0002-signing-and-verification.md)) |
| Replay de mensajes | `nonce` + `issued_at`/`expires_at` + `revision` monotónica |
| Robo de credencial del Operator | Identidad **mTLS por instancia**, credenciales de vida corta con rotación; sin credencial maestra ([ADR-0004](../adr/0004-operator-enrollment-and-identity.md)) |
| Fuga de secretos | Cifrado de sobre **age/X25519** a la clave pública de la instancia, en navegador y de un solo uso; OAuth/device flow preferente; prohibición en prompts cowork ([ADR-0005](../adr/0005-secrets-bundle-and-oauth.md)) |
| Cadena de suministro (pack malicioso) | Firma **Sigstore/Cosign** (keyless OIDC + Rekor) con verificación offline del bundle, alternativa **minisign/Ed25519** para air-gapped, SBOM/attestation, verificación antes de instalar, catálogo curado ([ADR-0002](../adr/0002-signing-and-verification.md)) |
| Brecha multi-tenant en el Hub | Aislamiento estricto por instancia; sin BD compartida de contenido; revisiones periódicas |
| Hub recibe datos de negocio | Frontera solo-Runtime; backups gestionados solo con consentimiento explícito y cifrado |
| Cambio crítico impuesto | Aprobación obligatoria del `superadmin` incluso en `stable` ([ADR-0007](../adr/0007-update-channels-and-rollout.md)) |

<a id="observability"></a>
## 9. Observabilidad y auditoría

- **Audit log dual:** toda orden aplicada y todo cambio de estado quedan en el audit log del Hub **y**
  de la instancia (principio P12). En la instancia el audit log es exportable (NDJSON, como RFC-002
  `/_console/audit`).
- **Telemetría de flota:** solo métricas de salud agregadas (versión, uptime, CPU/mem %, paquetes
  instalados, progreso de setup). Nunca contenido.
- **Trazabilidad:** blueprints y packs versionados; `questionnaire_hash`; `revision` de estado deseado.

<a id="failure"></a>
## 10. Modos de fallo, offline y recuperación ante desastres

- **Caída del Hub:** Runtime y Operator siguen operando en modo autónomo; el Hub es plano de control,
  no dependencia de disponibilidad del plano de datos.
- **Operator desconectado (kill switch):** la instancia sigue funcionando; se detienen solo las
  actualizaciones automatizadas.
- **Pérdida de conexión de red:** el Operator hace fallback a polling; reanuda al reconectar aplicando
  la `revision` más reciente.
- **Setup interrumpido:** el estado del `SetupPlan` persiste; el usuario reanuda exactamente donde lo
  dejó (criterio de aceptación del MVP).
- **DR:** el Runtime es la fuente de verdad de datos; backups gestionados (opcional, de pago, cifrado y
  consentido) o export/portabilidad OSS para self-hosted. El Hub puede reconstruir metadatos de flota
  desde los status-report de los Operators.

<a id="roadmap"></a>
## 11. Roadmap, no-goals, métricas y criterios de aceptación del MVP

### Roadmap por prioridad

| Fase | Contenido | Objetivo |
|---|---|---|
| **P0 (MVP)** | Cuestionario + motor de Blueprint en el Hub; generación de `nexus.blueprint.yaml`, `setup.plan.yaml`, `SETUP.md` y checklist humano; **handoff manual** (cowork o usuario ejecuta sin Operator); máquina de estados de tareas operativa aunque la ejecución sea manual | Validar que el cuestionario produce blueprints útiles y que el handoff a cowork funciona, sin control remoto |
| **P1 (Operator)** | Operator OSS: enrolamiento, conexión saliente, aplicación de estado deseado firmado, comandos acotados, telemetría | Automatizar lo que en P0 era manual |
| **P2 (Registry y packs)** | Registry con `nexus.pack.yaml`, ciclo de vida completo (instalar, validar, activar, rollback, overlays) | Extender instancias con contenido seguro y versionado |
| **P3 (Flota gestionada)** | Canales, matriz de compatibilidad, staged rollout, aprobación de críticos a escala de flota | Cerrar "mejoras centrales para todas las instancias" sin perder control |

### No-goals (explícitos)

Fuera del MVP y de P1: **marketplace público con transacciones**, **federación entre instancias**, y
**cualquier forma de ejecución remota arbitraria**. Los tres quedan fuera de alcance hasta que Operator
y Registry básicos estén validados en producción.

### Métricas de éxito

% de usuarios que completan cuestionario→blueprint; % de instancias blueprint→operativa sin soporte
humano; tiempo medio registro→primer Jarvis; % de tareas en `failed` sin reintento exitoso; reparto de
modalidades; tickets de soporte por instancia en el primer setup.

### Criterios de aceptación del MVP (P0)

1. Completar el cuestionario genera los **7 artefactos** del blueprint sin intervención manual.
2. Entregar `setup.plan.yaml` + `SETUP.md` a un cowork permite ejecutar cada tarea **sin ningún
   secreto en texto plano** en su contexto.
3. El `nexus.secrets.bundle` se **invalida tras la importación** exitosa; no queda copia reutilizable
   en el Hub.
4. Una tarea que supera el máximo de reintentos pasa a `failed` con motivo y opción de escalar.
5. Si el usuario cancela a mitad, al volver encuentra su plan **exactamente donde lo dejó**.

### Decisiones abiertas (resumen)

Nombre "Skull" (alias marca / "Agent Cognition Profile" formal — resuelto en el
[glosario](glossary.md)). **Resueltas 2026-07-19:** la **arquitectura criptográfica** es híbrida y está
aprobada —Sigstore/Cosign para artefactos públicos, Ed25519 (KMS/HSM) para estado deseado, mTLS por
instancia para transporte, minisign/Ed25519 para verificación offline y age/X25519 para cifrado de
secretos ([ADR-0002](../adr/0002-signing-and-verification.md))— y el **modelo de licencia por
componente** está aprobado (Apache-2.0 para OSS; propietario para Hub/servicios gestionados; SPDX
obligatorio por pack), con la relicencia del código existente **bloqueada** hasta la auditoría legal
([ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md)). **Aún abiertas:** pricing numérico;
decisión **CLA/DCO**; región de datos por defecto (preguntada explícitamente, sin default silencioso).
