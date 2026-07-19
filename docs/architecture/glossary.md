# Glosario formal — Portal Gestionado de NexusOS (`v1alpha1`)

Términos normativos del conjunto documental del portal gestionado. Donde un término tiene alias de
marca y término técnico formal, se indican ambos.

| Término | Definición | ¿Custodia datos de negocio? | ¿Se distribuye vía Registry? |
|---|---|---|---|
| **Hub** (Nexus Hub) | Plano de control **hospedado**: cuentas, facturación, cuestionario, motor de blueprint, estado de setup, metadatos de flota, catálogo. No contiene datos de negocio ni memoria. TARGET-STATE. | No | — |
| **Operator** (Nexus Operator) | Agente OSS junto a la instancia. Conexión **saliente**, reconcilia estado deseado firmado, instala packs, reporta salud. **Sin shell arbitrario.** TARGET-STATE. | No | — |
| **Runtime** (NexusOS Runtime / Platform) | Plano de datos **soberano**: Jarvis, espacios, áreas, agentes, meetings, memoria, usuarios, vault local. Opera sin Hub. Es Nexus Platform consolidado. | Sí | — |
| **Registry** (Nexus Registry) | Catálogo firmado y versionado de packs. Consultable con o sin Hub. TARGET-STATE. | No | — |
| **Instance** | Un despliegue de Runtime con identidad propia (`instance_id`). Aislada de las demás. | Sí | — |
| **Blueprint** | Arquitectura recomendada, versionada, emitida por el motor de blueprint a partir del cuestionario. Artefacto `nexus.blueprint.yaml`. | No | No |
| **SetupPlan** | Lista ordenada, con dependencias, de tareas derivadas de un blueprint. Artefacto `setup.plan.yaml`. | No | No |
| **SetupTask** | Tarea individual del SetupPlan, modelada como máquina de estados con owner, evidencia, reintento y rollback. | No | No |
| **Area** (Área) | Dominio funcional completo con coordinador, agentes especializados, reglas y **memoria propia**. Unidad que custodia memoria de dominio. | Sí | Sí |
| **Agent** (Agente) | Proceso con persona/voz que interactúa con usuarios u otros agentes dentro de un área. Opera sobre datos, no los define. | No directamente | Como parte de un pack |
| **Skull** / **Agent Cognition Profile** | **Alias de marca: "Skull"**; **término técnico formal: "Agent Cognition Profile"**. Perfil portable de cognición: instrucciones de sistema, política de modelo, tools/capacidades, esquema de memoria esperado y suite de evaluación. **Nunca contiene datos de negocio ni secretos**; es plantilla de comportamiento, no contenedor de estado. | No | Sí (solo o dentro de un pack) |
| **Sidecar** | Proceso asíncrono suscrito a eventos; produce artefactos en background sin bloquear al usuario. No es el custodio de la memoria principal. | Puede producir artefactos | Sí |
| **Flow** | Automatización o secuencia de pasos definida en el editor visual. | No | Sí |
| **Pack** | Unidad **atómica** de distribución del Registry: empaqueta cualquier combinación de áreas, agentes, skulls, flows y sidecars. Compone primitivas del Runtime; nunca es un runtime nuevo. Manifiesto `nexus.pack.yaml`. | Depende del contenido | Sí |
| **Overlay** | Capa de configuración aplicada **encima** de un pack sin editar sus archivos originales, de modo que una actualización no destruye la personalización (cf. `values.yaml`/Kustomize). | No | No |
| **Desired State** (Estado deseado) | Documento firmado y protegido contra replay que el Hub publica; el Operator reconcilia el delta contra el estado real. Contiene intents de capacidad acotada, nunca shell. | No | No |
| **Installation** | Registro de qué pack/versión está instalado en qué instancia. | No | No |

## Términos criptográficos y de licencia (`v1alpha1`, aprobados)

| Término | Definición | Uso normativo |
|---|---|---|
| **Sigstore / Cosign** | Firma keyless (OIDC) con log de transparencia (Rekor) y verificación offline del bundle. | **Solo** artefactos públicos: releases, imágenes, packs del Registry público, SBOM, provenance. |
| **Ed25519** | Firma de curva elíptica ligera y determinista. | **Estado deseado** e intents del plano de control Hub→Operator; claves en KMS/HSM; verificación offline con clave pineada. |
| **mTLS por instancia** | TLS mutuo con certificado por instancia, de vida corta y rotado. | **Transporte y enrolamiento** del Operator; identidad distinta de la clave de firma. |
| **Minisign** | Firma Ed25519 simple basada en fichero, sin infraestructura. | Verificación **offline/air-gapped** de packs (`offline_signature`). |
| **age / X25519** | Cifrado de sobre a destinatarios de clave pública X25519. **Solo cifrado, nunca firma.** | `nexus.secrets.bundle`; recipiente público en el manifiesto, ciphertext fuera de banda. |
| **Trust domain** | Raíz de confianza contra la que el verificador resuelve una clave (`hub.nexusos.dev`, `sigstore-public-good`, CA mTLS, claves minisign). | Campo `trust_domain` en `Signature`/`hub_public_key`. |
| **Provenance / SBOM attestation** | Bundle Sigstore + attestation de SBOM firmado que prueba el origen del artefacto. | Bloque `provenance` de `nexus.pack.yaml`. |
| **SPDX license** | Expresión SPDX que identifica la licencia del **contenido**. **Obligatoria por pack.** | `metadata.license`; no concede derechos de **marca** (bloque `trademark`). |
| **Break-glass** | Aplicación excepcional de estado deseado con clave Ed25519 de emergencia pineada si el KMS del Hub no está disponible; auditada y con rotación forzada posterior. | Ver [ADR-0002](../adr/0002-signing-and-verification.md). |

**Notas de coherencia con el repo actual:** `artifact_type` de una plantilla de agente
(`agent | sidecar | skill`) se define en `console/agent_templates/_schema.md`; un **skill** es una
capacidad reutilizable que agentes y sidecars invocan (no runnable independiente). Las áreas
disponibles hoy en el wizard están en `console/app/models/wizard.py` (`AVAILABLE_AREAS`).
