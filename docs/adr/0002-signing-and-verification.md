# ADR-0002: Firma y verificación de documentos de estado deseado y paquetes

- **Estado:** Aceptada en principio; **proveedor de firma pendiente de evaluación técnica**
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0001](0001-hub-operator-runtime-registry-split.md), [ADR-0006](0006-nexus-pack-format.md), esquemas [`common.defs`](../schemas/v1alpha1/common.defs.schema.json), [`desired-state`](../schemas/v1alpha1/desired-state.schema.json)

## Contexto

El canal Hub↔Operator y el Registry transmiten instrucciones y contenido que, si se manipulan,
comprometen la instancia. Necesitamos integridad, autenticidad y protección contra repetición (replay)
sin introducir un shell remoto ni depender de la disponibilidad del Hub para verificar.

## Decisión

- **Todo documento de estado deseado y todo pack se firman.** El Operator/Runtime verifica la firma
  **antes** de aplicar o instalar. Sin firma válida, no se aplica.
- **Modelo de firma** (definido en `common.defs.schema.json#/$defs/Signature`): `algorithm`,
  `key_id`, `value`, `canonicalization` y `certificate_chain` opcional.
- **Canonicalización** del payload antes de firmar (`jcs` / `json-c14n` / `cbor`) para que la
  verificación sea determinista.
- **Protección contra replay** (`common.defs.schema.json#/$defs/ReplayGuard`): cada mensaje firmado
  incluye `nonce` + `issued_at` + `expires_at`; el verificador rechaza nonces repetidos dentro de la
  ventana y mensajes expirados. El estado deseado además lleva `revision` monotónica: el Operator
  ignora revisiones inferiores a la última aplicada.
- **Verificación offline:** la clave pública de firma del Hub se entrega en el enrolamiento
  (`enrollment.response`), de modo que el Operator puede verificar aunque el Hub esté caído.

## Decisión abierta (bloqueante para implementación, no para estas ADR)

El **esquema concreto de firma** queda entre dos candidatos, a resolver con una prueba de concepto:

| Opción | Ventajas | Riesgos |
|---|---|---|
| **sigstore / cosign** (keyless, transparency log) | Estándar de industria para supply-chain; buena para packs del Registry; trazabilidad pública | Dependencia de infraestructura de transparencia; más pesado para mensajes efímeros de estado deseado |
| **age envelopes / Ed25519 detached** | Simple, ligero, ideal para mensajes efímeros y cifrado a clave pública de instancia | Sin transparency log; hay que construir la distribución/rotación de claves |

**Recomendación de evaluación:** cosign para *packs* (artefactos publicados, cadena de suministro) y
Ed25519 detached + nonce para *estado deseado* (mensajes efímeros). El esquema soporta ambos vía el
enum `algorithm`.

## Consecuencias

- Integridad y autenticidad end-to-end; imposibilidad de replay dentro de la ventana.
- Coste: gestión de claves y su rotación (ver [ADR-0004](0004-operator-enrollment-and-identity.md)).
- Los esquemas ya reservan los campos; la elección de proveedor no cambia el contrato.

## Criterios de evaluación para cerrar la decisión

1. Verificación 100% offline en el Operator.
2. Rotación de claves sin downtime.
3. Footprint aceptable para mensajes de estado deseado de alta frecuencia.
4. Auditoría/transparencia para packs publicados.
