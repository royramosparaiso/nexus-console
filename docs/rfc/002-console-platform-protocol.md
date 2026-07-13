# RFC-002: Protocolo Console ↔ Platform

**Estado:** Draft v0.1
**Autor:** Rodrigo Ramos Paraiso (Ironbat Digital)
**Fecha:** 2026-07-13
**Documento hermano:** RFC-001 (Nexus como framework instalable), Specs v0.6 §2quater

## Motivación

A partir de Nexus OS v0.6, el framework se distribuye en dos productos:

- **Nexus Console** (este repo) — plano de control.
- **Nexus Platform** (repo `ironbat-jarvis`, futuro rename `nexus-platform`) — plano de datos.

Ambos hablan por HTTP + JWT firmado. Este RFC formaliza el protocolo. El mismo protocolo se reusa en v2 para federación cross-instance entre Platforms (una Platform con `federation_grant` actúa como emisor válido en otra Platform, ver Specs §5.2).

## Identidad y auth

- Cada Console tiene un par de claves `console_kid` + Ed25519.
- Cada Platform, en el bootstrap inicial, registra la clave pública de su Console de referencia.
- Multi-console: una Platform puede aceptar comandos de varias Consoles con roles distintos (`primary`, `readonly-monitor`, `backup-owner`).
- Los comandos son JWT firmados (EdDSA) con `iss`, `aud=instance_id`, `exp` corto (60 s), y `payload.cmd`.

## Endpoints en Platform

- `POST /_bootstrap` — solo válido antes del primer registro. Recibe `nexus.instance.yaml` + clave pública de Console. Idempotente antes del bootstrap, rechazado después.
- `POST /_console/command` — endpoint autenticado para comandos operacionales:
  - `set_llm_provider`, `install_area`, `uninstall_area`, `deploy_agent`, `undeploy_agent`, `update_ceiling`, `rotate_secret`, `pause_instance`, `resume_instance`, `create_space`, `delete_space`, `grant_cross_instance_access`, `kill_switch_agent`, `upgrade_platform`.
- `GET /_console/status` — versión Platform, arquitectura activa, health.
- `GET /_console/audit` — export streaming NDJSON del audit log.

## Endpoints en Console

- `POST /instances` — crear instancia (dispara wizard + deploy).
- `GET /instances` — listar instancias con salud.
- `POST /instances/{iid}/command` — proxy firmado a Platform.
- `POST /invitations` — crear invitación cross-instance.
- `POST /agents/factory` — publicar agente al catalog.

## Notificaciones Platform → Console

Platform notifica eventos a Console vía `POST` firmado a `{console_url}/_platform/notify`:

- `budget_alert`, `governance_alert`, `agent_stuck`, `cross_instance_invitation_received`, `upgrade_available`.

## Sin acoplamiento fuerte

HTTP + JWT. Console y Platform pueden estar en máquinas y redes distintas. Console **nunca** accede a la BD de Platform directamente. Compatibilidad backward de una versión minor.

## No incluido en v0.1

- Handshake mutual TLS (postponed a v0.2).
- DPoP (postponed a federación v2).
- Discovery público `/.well-known/nexus-instance.json` (federación v2).

## Cambios pendientes

- [ ] Definir esquema exacto JSON de cada comando (`cmd_schema.md`).
- [ ] Definir formato exacto del `nexus.instance.yaml`.
- [ ] Definir política de rotación de `console_kid`.
