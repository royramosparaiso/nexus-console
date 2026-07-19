# Spec H: Seguridad, confianza, firma y secretos

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2` (reutiliza crypto `v1alpha1`)
- **Fecha:** 2026-07-19
- **Contratos:** [`common.defs` v1alpha1](../schemas/v1alpha1/common.defs.schema.json), [`common.defs` v1alpha2](../schemas/v1alpha2/common.defs.schema.json), [`secrets-bundle-manifest`](../schemas/v1alpha1/secrets-bundle-manifest.schema.json), [`entitlement`](../schemas/v1alpha2/entitlement.schema.json)
- **Relacionadas:** [ADR-0002](../adr/0002-signing-and-verification.md), [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md)

## 1. Problema y contexto

El modelo de confianza debe soportar artefactos públicos, plano de control, verificación offline y
cifrado de secretos, cada uno con la primitiva adecuada, sin mezclar responsabilidades.

## 2. Objetivos

- Fijar el algoritmo por caso de uso y prohibir usos incorrectos por contrato.
- Verificación offline de packs y entitlements.
- Secretos por referencia, nunca en claro en fixtures ni manifiestos.

## 3. No-objetivos

- Custodia de secretos en el Hub. Firmar con `age`. Verificación online obligatoria.

## 4. Actores

- **Hub KMS/HSM**, **Operator/Runtime** (verificador), **autores de packs**, **CA mTLS**.

## 5. Conceptos y modelo de datos (matriz de crypto)

| Uso | Primitiva | Regla |
|---|---|---|
| Artefactos públicos (releases, imágenes, packs públicos, SBOM) | **Sigstore/Cosign** | Keyless + Rekor; solo público. |
| Estado deseado e **entitlements** | **Ed25519** (KMS/HSM) | Verificación offline con clave pineada + `trust_domain`. |
| Transporte y enrolamiento | **mTLS por instancia** | Identidad distinta de la clave de firma. |
| Verificación offline de packs | **Minisign** | `offline_signature`; sin infraestructura. |
| Cifrado de secretos | **age / X25519** | Solo cifrado, **nunca** firma. |

## 6. Requisitos funcionales

- **P0:** verificar Cosign (público) y minisign/Ed25519 (offline); rechazar `age` como firma.
- **P1:** entitlements Ed25519 con `trust_domain`; secrets bundle age/X25519.
- **P2:** break-glass Ed25519 auditado ([ADR-0002](../adr/0002-signing-and-verification.md)).

## 7. Flujos y transiciones de estado

1. Publicación: firmar artefacto (Cosign/minisign) y adjuntar provenance/SBOM.
2. Verificación: resolver clave por `trust_domain`; validar firma offline.
3. Secretos: cifrar a destinatario X25519; el manifiesto lleva solo referencia, no ciphertext.

## 8. Fronteras de API/contrato

- `Signature` (common.defs) restringe algoritmos; `secrets-bundle-manifest` prohíbe ciphertext/plaintext
  y exige esquema age; `entitlement.signature` fija ed25519 + trust_domain.

## 9. Seguridad y privacidad

- Ningún valor de secreto en fixtures (test `test_no_plaintext_secret_values`). Solo `signature.value`
  (base64 de firma, no secreto) y claves públicas permitidas.

## 10. Comportamiento ante fallo/offline

- Verificación 100% offline para packs y entitlements. Si KMS del Hub cae, break-glass auditado.

## 11. Telemetría/observabilidad

- Auditoría de verificaciones y de uso de break-glass; rotación forzada posterior.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** una `Signature` con `algorithm: age`, **when** se valida, **then** se rechaza.
- **Given** un `secrets-bundle-manifest` con `ciphertext`, **when** se valida, **then** se rechaza.
- **Given** un manifiesto con `scheme: jwe`, **when** se valida, **then** se rechaza (debe ser age).
- **Given** un `desired-state` con `sigstore-cosign`, **when** se valida, **then** se rechaza (pin
  Ed25519).

## 13. Métricas de éxito

- Cero fugas de secreto en artefactos. Cero firmas con primitiva incorrecta. Verificación offline total.

## 14. Dependencias

- Todas las specs consumen esta matriz. [ADR-0002](../adr/0002-signing-and-verification.md).

## 15. Migración/versionado

- `v1alpha2` reutiliza los `$defs` crypto de `v1alpha1` por `$id` absoluto; no rompe primitivas.

## 16. Preguntas abiertas

- Proveedor KMS/HSM; política de rotación de claves y `trust_domain`; gestión de Rekor privado si aplica.
