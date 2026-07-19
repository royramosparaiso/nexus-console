# ADR-0008: Frontera OSS/comercial y decisión de licencia

- **Estado:** Aceptada la **frontera**; **licencia PENDIENTE de decisión legal formal**
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [frontera OSS/comercial](../architecture/product-oss-boundary.md); `LICENSE` (hoy MIT en Console)

## Contexto

Nexus OS declara un espíritu "all open". El portal gestionado introduce servicios de pago (Hub,
provisioning, orquestación de secretos, backups, catálogo curado). Hay que fijar qué queda en OSS y
qué se ofrece como servicio, **sin** retener fuera del OSS nada relacionado con seguridad, exportación
o portabilidad. La elección de licencia tiene implicaciones legales y de negocio que exceden lo técnico.

## Decisión (frontera)

- **OSS (siempre):** Runtime completo, Operator, Admin API local, esquemas de manifiesto
  (`nexus.pack.yaml`, `nexus.blueprint.yaml`, `setup.plan.yaml`), SDK/CLI, verificador e instalador de
  packs, cliente de Registry comunitario, wizard/generador local básico, y **toda** capacidad de
  seguridad, exportación y portabilidad.
- **Hospedado (de pago):** Hub gestionado, provisioning, broker OAuth centralizado, orquestación de
  secretos cifrados a escala, monitorización/alertas de flota, backups gestionados, actualizaciones de
  flota coordinadas, catálogo curado y verificado, facturación, soporte y SLA.
- **Regla de diseño explícita:** un usuario autohospedado puede verificar firmas, exportar su instancia
  completa y auditar su sistema **sin depender de ningún componente de pago**. Lo que se cobra es
  comodidad operativa, nunca soberanía ni seguridad básica.

## Decisión de licencia — PENDIENTE (no es consejo legal)

Se registra el trade-off; **no se prescribe** la elección. Debe resolverse con asesoría legal formal
**antes de publicar el repositorio** de Runtime/Operator; no bloquea el MVP (que no requiere publicar
el código todavía).

| Opción | Ventajas | Riesgos |
|---|---|---|
| **Apache-2.0** (todo el proyecto) | Máxima adopción; fricción mínima para empresas; coherente con "all open" | Un competidor puede ofrecer un SaaS propio sin retornar nada |
| **AGPL + licencia comercial dual** | Protege contra SaaS competidor sin abrir código; vía de ingresos legal clara | Puede frenar adopción empresarial; más complejo de comunicar |

**Criterios de evaluación para cerrar la decisión:** (1) objetivo de adopción vs. protección del
modelo de negocio; (2) apetito de la comunidad por copyleft de red; (3) compatibilidad con la
integración empresarial esperada; (4) coherencia con la licencia actual de Console (MIT) y de los
packs.

## Consecuencias

- La frontera es estable e implementable ya; la licencia se puede fijar más tarde sin rediseñar la
  frontera.
- Riesgo si se retrasa demasiado: incertidumbre para contribuidores externos. Mitigación: comunicar la
  frontera con transparencia desde el primer commit público.
