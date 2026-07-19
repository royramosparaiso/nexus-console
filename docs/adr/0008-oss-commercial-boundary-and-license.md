# ADR-0008: Frontera OSS/comercial y licencia por componente

- **Estado:** **Aceptada** (modelo de licencia por componente aprobado 2026-07-19). **La relicencia efectiva del código existente permanece BLOQUEADA hasta completar la auditoría de titularidad/contribución descrita abajo.**
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [frontera OSS/comercial](../architecture/product-oss-boundary.md); `LICENSE` (hoy MIT en Console); [ADR-0002](0002-signing-and-verification.md), [ADR-0006](0006-nexus-pack-format.md)

## Contexto

Nexus OS declara un espíritu "all open". El portal gestionado introduce servicios de pago (Hub,
provisioning, orquestación de secretos, backups, catálogo curado). Hay que fijar qué queda en OSS y qué
se ofrece como servicio, **sin** retener fuera del OSS nada relacionado con seguridad, exportación o
portabilidad. La elección de licencia tiene implicaciones legales y de titularidad que exceden lo
técnico y que **no** pueden ejecutarse unilateralmente sobre código con múltiples titulares.

## Decisión — licencia separada por componente (aprobada)

- **Apache-2.0** (OSS permisiva) para: **NexusOS Runtime**, **Nexus Operator**, **CLI**, **SDK**,
  **esquemas/contratos públicos** (`nexus.pack.yaml`, `nexus.blueprint.yaml`, `setup.plan.yaml`, etc.),
  **verificador e instalador de packs**, **cliente de Registry comunitario** y las **capacidades
  básicas locales** de generador/admin.
- **Propietario (comercial)** para: **Nexus Hub** (SaaS hospedado), **facturación**, **provisioning y
  orquestación gestionados**, **operaciones de flota** y **servicios gestionados/catálogo curado**.
- **Packs:** cada paquete declara su **propia** licencia. Puede ser Apache/comunidad,
  comercial/propietaria (`LicenseRef-…`) u otra licencia compatible declarada. **Todo pack DEBE
  declarar metadatos de licencia SPDX** (`metadata.license`, ahora **obligatorio** en
  `nexus.pack.schema.json`).
- **Regla de soberanía:** **seguridad, exportación, portabilidad y operación self-hosted permanecen en
  el lado OSS.** Un usuario autohospedado puede verificar firmas, exportar su instancia completa y
  auditar su sistema sin depender de ningún componente de pago.
- **Marca:** la política de marcas de **NexusOS/Ironbat es independiente de la licencia de código**. La
  licencia de contenido de un pack **no** concede derechos de marca (reflejado en
  `nexus.pack.schema.json#/properties/metadata/properties/trademark`).

## SPDX y gobernanza de contribución

- **Regla SPDX:** cada componente y cada pack declara una expresión SPDX válida. Componentes OSS:
  `Apache-2.0`. Componentes/paquetes propietarios: `LicenseRef-Ironbat-Commercial-<versión>`. El
  esquema valida la forma de la expresión; la corrección legal se audita (abajo).
- **CLA vs DCO — decisión REQUERIDA antes de aceptar contribuciones externas al código Apache-2.0.**
  Debe elegirse formalmente (recomendación a evaluar: DCO ligero para adopción, CLA si se quiere
  flexibilidad de relicencia futura). Es un **prerequisito de gobernanza**, no una decisión técnica.

## Relicencia del código existente — BLOQUEADA hasta auditoría

**No se sustituye silenciosamente la licencia MIT actual** ni se afirma que el código mixto de Console
ya está relicenciado. El `LICENSE` raíz **sigue siendo MIT** y **todos** los archivos actuales de
`console/` conservan MIT hasta ejecutar la migración. Procedimiento de migración concreto:

1. **Auditoría de titularidad/contribución (BLOQUEANTE):** identificar a todos los titulares de derechos
   y contribuidores del código actual (git history + cualquier código importado, p. ej. migrado desde
   `ironbat-jarvis`) y su procedencia de licencia.
2. **Matriz ruta→licencia:** mapear cada directorio/módulo a su licencia objetivo (ver tabla abajo)
   antes de tocar cabeceras.
3. **Consentimiento:** obtener el acuerdo de relicencia de cada titular para las partes que pasan a
   Apache-2.0, o reescribir/aislar el código sin consentimiento.
4. **Decisión CLA/DCO** aplicada de aquí en adelante.
5. **Aplicación:** añadir cabeceras SPDX por archivo, `LICENSE` por componente y actualizar el `LICENSE`
   raíz solo cuando la migración de ese componente esté completa y auditada.
6. **Asesoría legal formal** valida los pasos 1–5 **antes** de publicar los repos de Runtime/Operator.

### Matriz ruta → licencia objetivo (target-state)

| Ruta / componente | Licencia objetivo | Estado hoy |
|---|---|---|
| `docs/schemas/**` (contratos públicos) | Apache-2.0 | MIT (raíz) hasta migración |
| Runtime / Operator / CLI / SDK (repos futuros) | Apache-2.0 | No publicado |
| Verificador/instalador de packs, cliente Registry comunitario | Apache-2.0 | No publicado |
| `console/**` (código actual, mixto) | Por decidir tras auditoría (Apache-2.0 objetivo salvo módulos Hub) | **MIT — sin cambios** |
| Hub, billing, provisioning/orquestación gestionada, operaciones de flota | Propietario (`LicenseRef-Ironbat-Commercial`) | No publicado |
| Packs | Declarada por paquete (SPDX obligatorio) | N/A |

## Consecuencias

- La frontera y el modelo de licencia por componente son estables e implementables ya; la publicación de
  Runtime/Operator queda condicionada a la auditoría legal.
- No hay riesgo de relicencia inválida: el código existente permanece MIT hasta consentimiento
  auditado.
- Riesgo: si la auditoría o la decisión CLA/DCO se retrasan, se frena la aceptación de contribuciones
  externas. Mitigación: comunicar la frontera y el objetivo por componente desde el primer commit
  público y arrancar la auditoría pronto.

## Prerequisitos legales no discrecionales (antes de relicenciar)

1. Auditoría completa de titularidad/contribución del código actual (incluye código migrado).
2. Consentimiento de relicencia de todos los titulares para las partes Apache-2.0.
3. Decisión formal **CLA o DCO**.
4. Revisión de asesoría legal de la matriz ruta→licencia y de la política de marca separada.
