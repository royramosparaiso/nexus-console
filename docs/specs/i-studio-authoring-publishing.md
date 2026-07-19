# Spec I: Studio: autoría y publicación

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-19
- **Contratos:** [`nexus.pack.schema.json`](../schemas/v1alpha1/nexus.pack.schema.json), [`package-access-policy.schema.json`](../schemas/v1alpha2/package-access-policy.schema.json)
- **Relacionadas:** [Spec E](e-registry-catalog-distribution.md), [Spec F](f-package-artifact-model.md)

## 1. Problema y contexto

La autoría cubre cuatro lanes: creación verificada de Ironbat, overlays locales del usuario, publicación
comunitaria y publicación privada de organización. Cada una tiene distinto nivel de verificación y de
distribución, sin restringir el OSS.

## 2. Objetivos

- Permitir crear, versionar, firmar y publicar packs por cualquiera de los cuatro lanes.
- Soportar **overlays locales** no destructivos sobre packs de terceros.
- Mapear cada lane a su `publisher_verification` y visibilidad.

## 3. No-objetivos

- DRM. Bloquear el forking. Publicar sin firma.

## 4. Actores

- **Ironbat (verificado/oficial)**, **autor comunitario**, **organización**, **usuario local**.

## 5. Conceptos y modelo de datos

| Lane | `publisher_verification` | Visibilidad típica | Distribución |
|---|---|---|---|
| Creación verificada Ironbat | `verified` / `official` | verified-premium o public | catálogo curado |
| Overlay local del usuario | n/a (no se publica) | local | no se distribuye |
| Publicación comunitaria | `community` | community | mirror abierto |
| Privada de organización | `verified` | private-organization | grant de vida corta |

## 6. Requisitos funcionales

- **P0:** autoría local + overlays no destructivos; firmar y validar.
- **P1:** publicación comunitaria (carril abierto) y verificada (curado).
- **P2:** publicación privada de organización con entitlement.

## 7. Flujos y transiciones de estado

1. Autor crea artefactos y `nexus.pack.yaml`; aplica overlays sin editar el pack base.
2. Firma (minisign/Cosign) y elige lane -> `package-access-policy` coherente.
3. Publica: abierto (directo/mirror) o cerrado (grant + entitlement).

## 8. Fronteras de API/contrato

- Produce `nexus.pack` + `package-access-policy`. Los overlays son configuración local, no se publican.

## 9. Seguridad y privacidad

- Firma obligatoria; skulls sin datos/secretos; SPDX obligatorio; marca independiente de la licencia.

## 10. Comportamiento ante fallo/offline

- Autoría y overlays funcionan offline. La publicación a carriles cerrados requiere conexión al Hub.

## 11. Telemetría/observabilidad

- Auditoría local de publicación; sin datos de negocio hacia el Hub.

## 12. Criterios de aceptación (Given/When/Then)

- **Given** un overlay local, **when** se actualiza el pack base, **then** la personalización no se
  pierde (overlay no destructivo).
- **Given** un pack comunitario, **when** se publica, **then** queda en carril abierto, replicable y sin
  cuenta.
- **Given** un pack privado de organización, **when** se publica, **then** exige entitlement y grant de
  vida corta.

## 13. Métricas de éxito

- 100% de packs firmados y con SPDX. Overlays no destructivos verificados. Forking del OSS posible.

## 14. Dependencias

- [Spec E](e-registry-catalog-distribution.md), [Spec F](f-package-artifact-model.md), [Spec H](h-security-trust-signing-secrets.md).

## 15. Migración/versionado

- Reutiliza `nexus.pack` (`v1alpha1`) extendido; overlays ya existen conceptualmente en el glosario.

## 16. Preguntas abiertas

- UX del editor de Studio (fuera de contrato); política de verificación `official` vs `verified`.
