# ADR-0004: Enrolamiento del Operator, identidad de instancia y rotación de credenciales

- **Estado:** Aceptada (contrato `v1alpha1`)
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0001](0001-hub-operator-runtime-registry-split.md), [ADR-0002](0002-signing-and-verification.md); esquemas [`enrollment.request`](../schemas/v1alpha1/enrollment.request.schema.json), [`enrollment.response`](../schemas/v1alpha1/enrollment.response.schema.json)

## Contexto

El Operator necesita una identidad propia por instancia y credenciales que no sean maestras ni de
larga duración. La conexión debe ser **saliente** (el Hub nunca inicia hacia la instancia) para no
exigir puertos entrantes en la infraestructura del usuario. RFC-002 ya establece que cada Platform
registra la clave pública de su Console; esta ADR generaliza ese modelo al par Hub↔Operator.

## Decisión

- **Conexión saliente exclusiva:** mTLS sobre WebSocket, o polling si la red bloquea conexiones
  persistentes. El Hub nunca inicia conexión hacia la instancia.
- **Enrolamiento por token de un solo uso:**
  1. El Hub genera un **token de un solo uso y vida corta** (`POST /v1/instances/{id}/enrollment-token`).
  2. El Operator genera **localmente** un par de claves (la privada nunca sale de la instancia) y
     envía `EnrollmentRequest` (`enrollment.request.schema.json`) con la clave pública y el token.
  3. El Hub responde `EnrollmentResponse` (`enrollment.response.schema.json`) con `instance_id`, una
     **credencial de vida corta** (`mtls_cert` o `bearer_jwt`) con `rotation_policy`, y su **clave
     pública de firma** (para verificación offline del estado deseado).
- **Rotación:** la credencial expira (`expires_at`) y el Operator la renueva antes de expirar
  (`rotate_before_expiry_seconds`). **Nunca** existe una credencial maestra de larga duración en la
  instancia.
- **Kill switch:** el usuario puede desconectar el Operator del Hub de forma inmediata e irreversible
  desde el lado de la instancia; la instancia sigue operando en modo autónomo.
- **Modo offline:** el Operator es opcional; sin él la instancia funciona igual, solo sin
  actualizaciones automatizadas del Hub.
- **Auditoría:** el enrolamiento y cada rotación quedan en el audit log de Hub e instancia.

## Consecuencias

- No se exponen puertos entrantes; el token inicial no es reutilizable; el compromiso de una
  credencial de vida corta tiene ventana limitada.
- Coste: implementar rotación robusta y manejo de expiración/reintentos.

## Alternativas consideradas

- **Credencial estática de larga duración:** rechazada; riesgo de exfiltración persistente.
- **Conexión iniciada por el Hub:** rechazada; exige puertos entrantes y rompe el modelo saliente.
