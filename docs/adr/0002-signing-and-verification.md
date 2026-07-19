# ADR-0002: Firma y verificación de documentos de estado deseado y paquetes

- **Estado:** **Aceptada** (arquitectura criptográfica híbrida aprobada 2026-07-19)
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0001](0001-hub-operator-runtime-registry-split.md), [ADR-0004](0004-operator-enrollment-and-identity.md), [ADR-0005](0005-secrets-bundle-and-oauth.md), [ADR-0006](0006-nexus-pack-format.md), esquemas [`common.defs`](../schemas/v1alpha1/common.defs.schema.json), [`desired-state`](../schemas/v1alpha1/desired-state.schema.json)

## Contexto

El canal Hub↔Operator y el Registry transmiten instrucciones y contenido que, si se manipulan,
comprometen la instancia. Necesitamos integridad, autenticidad y protección contra repetición (replay)
sin introducir un shell remoto ni depender de la disponibilidad del Hub —ni de un log público de
transparencia— para poder verificar. Los distintos flujos tienen requisitos distintos: los packs
publicados exigen trazabilidad de cadena de suministro; los mensajes de estado deseado son efímeros y
de alta frecuencia y deben verificarse aunque no haya red pública; el transporte del Operator necesita
identidad mutua; los secretos requieren cifrado a clave pública de instancia.

## Decisión — arquitectura híbrida (aprobada)

Se adopta una separación explícita **por caso de uso**. Un algoritmo nunca se reutiliza fuera de su
dominio; en particular **`age` es cifrado, nunca firma**.

1. **Sigstore / Cosign** para artefactos públicos: releases, imágenes de contenedor, packs del Registry
   público, SBOMs y attestations de provenance. Soporta **OIDC keyless** para CI/publishers y
   **verificación offline del bundle** (`.sigstore` con certificado + prueba de inclusión). Trust root:
   `sigstore-public-good` (Fulcio + Rekor).
2. **Ed25519** para los documentos de **estado deseado** y los intents privados del plano de control
   Hub→Operator. Las claves de firma se custodian en **KMS/HSM** donde el despliegue es gestionado.
   **No se requiere disponibilidad de Sigstore ni de un transparency log** para la operación normal
   Hub↔Operator: el Operator fija (pin) la clave pública del Hub durante el enrolamiento y verifica
   100% offline.
3. **Identidad mTLS por instancia** para el transporte y el enrolamiento del Operator: certificados de
   **vida corta** con **rotación** antes de expirar (ver [ADR-0004](0004-operator-enrollment-and-identity.md)).
   La identidad mTLS (`spiffe://…/instance/inst_…`) es distinta de la clave de firma de estado deseado.
4. **Minisign / Ed25519** como vía de **verificación offline/self-hosted** de packs, sin depender de la
   infraestructura Sigstore. El pack puede llevar `offline_signature` (minisign) además de la firma
   Sigstore primaria.
5. **age / X25519** para el **cifrado de sobre** de `nexus.secrets.bundle`
   ([ADR-0005](0005-secrets-bundle-and-oauth.md)). age cifra a la clave pública X25519 de la instancia;
   **jamás firma** un paquete ni un mensaje.

### Reflejo en los contratos `v1alpha1`

- `common.defs#/$defs/Signature.algorithm` = `{ed25519, ecdsa-p256, sigstore-cosign, minisign}`.
  **`age` no está en el enum** (imposible firmar con age por construcción). Campos añadidos:
  `trust_domain`, `key_custody` (`kms|hsm|keyless_oidc|local_file`) y `transparency`
  (`TransparencyLogEntry`: log Rekor, índice, emisor OIDC, identidad de certificado).
- `desired-state.signature` está **restringido a `ed25519`** vía `allOf`, con `trust_domain`
  **obligatorio** y `key_custody ∈ {kms, hsm, local_file}`. Rechaza `sigstore-cosign`, `minisign` y
  `age`.
- `nexus.pack`: `signature` primaria (sigstore-cosign para el Registry público), `offline_signature`
  restringida a `{minisign, ed25519}`, y bloque `provenance` (bundle Sigstore + attestation de SBOM).
- `enrollment.response.hub_public_key.algorithm` = `{ed25519, ecdsa-p256}` (**sin** sigstore-cosign: la
  clave del plano de control no es keyless); `credential.mtls_identity` para la identidad de transporte.
- `secrets-bundle-manifest.encryption` fija `scheme: age` y exige `age_recipient` (X25519 público).

## Trust roots, rotación, revocación y break-glass

- **Trust roots:** (a) `sigstore-public-good` para artefactos públicos; (b) clave(s) Ed25519 del Hub
  fijadas por el Operator para estado deseado; (c) CA mTLS del Hub para transporte; (d) clave(s)
  minisign publicadas para verificación offline.
- **Rotación:** claves de firma del Hub rotadas en KMS con solapamiento (el `enrollment.response` y un
  endpoint de rotación entregan la nueva `key_id`/`public_key` antes de retirar la anterior);
  certificados mTLS de vida corta con `rotate_before_expiry_seconds`. Sin downtime.
- **Revocación:** lista de `key_id` revocadas distribuida en el estado deseado firmado y en el
  enrolamiento; para Sigstore, revocación vía identidad de certificado/Fulcio y expiración corta.
- **Protección contra replay:** `ReplayGuard` (`nonce` + `issued_at` + `expires_at`) en cada mensaje
  firmado; el estado deseado añade `revision` monotónica (el Operator ignora revisiones inferiores a la
  última aplicada).
- **Transparencia:** obligatoria para artefactos públicos (inclusión en Rekor verificable offline);
  **deliberadamente ausente** para el estado deseado privado.
- **Break-glass:** si el KMS del Hub no está disponible, el operador puede aplicar un estado deseado
  firmado con una clave Ed25519 de emergencia `key_custody: local_file` previamente pineada y auditada;
  el uso queda en el log de auditoría y fuerza rotación posterior. El **kill switch** del Operator
  ([ADR-0001](0001-hub-operator-runtime-registry-split.md)) permanece disponible en todo momento.

## Verificación offline y modos de fallo

- **Estado deseado:** verificable sin red pública (clave del Hub pineada). Si la firma no valida o el
  `ReplayGuard` expiró/repite, **no se aplica**; el Operator sigue en el último estado bueno conocido.
- **Packs:** verificables online (Sigstore/Rekor) u offline (minisign/Ed25519 + bundle con prueba de
  inclusión). Sin verificación válida, **no se instala**.
- **Transporte:** si la identidad mTLS caduca y no se puede rotar, el Operator opera en modo autónomo
  con el último estado deseado aplicado hasta recuperar conexión.

## Consecuencias

- Integridad y autenticidad end-to-end; imposibilidad de replay dentro de la ventana; trazabilidad
  pública para la cadena de suministro **sin** acoplar el plano de control a un log público.
- Coste: operar KMS/HSM para las claves del Hub, una CA mTLS y la publicación de claves minisign; más
  superficie de gestión de claves y rotación.
- Los esquemas ya codifican estas reglas; los tests
  (`console/tests/test_managed_platform_schemas.py`) prueban que age no firma, que el estado deseado
  exige Ed25519 + `trust_domain` y rechaza Sigstore, que `offline_signature` rechaza sigstore-cosign y
  que el manifiesto de secretos fija age/X25519 y prohíbe ciphertext.

## Rollout y migración

- **P0 (Hub):** firma Ed25519 en KMS para estado deseado; publicación de packs con Sigstore.
- **P1 (Operator):** pin de clave del Hub en el enrolamiento; verificación offline; mTLS de transporte.
- **P2 (Registry/offline):** `offline_signature` minisign y bundles Sigstore descargables para
  air-gapped.
- Compatibilidad: `v1alpha1` es alfa; cualquier cambio de enum/campo se documenta aquí y en
  `docs/schemas/README.md` y se refleja en todos los fixtures.
