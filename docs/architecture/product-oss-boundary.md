# Frontera producto / open-source y forma de pricing

- **Estado:** Frontera aprobada · **licencia y pricing numérico PENDIENTES**
- **Versión de arquitectura:** `v1alpha1`
- **Fecha:** 2026-07-19
- **Relacionadas:** [ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md)

## Regla de diseño explícita

**No se retiene fuera del OSS nada relacionado con seguridad, exportación o portabilidad.** Un usuario
autohospedado puede verificar firmas de packs, exportar su instancia completa y auditar su propio
sistema sin depender de ningún componente de pago. Lo que se cobra es **comodidad operativa**
(gestión, soporte, catálogo curado), **no** la soberanía ni la seguridad básica.

## Qué es OSS y qué es hospedado

| OSS (siempre disponible) | Hospedado (servicio de pago) |
|---|---|
| Runtime completo | Aprovisionamiento gestionado (Managed) |
| Operator | Hub hospedado |
| Admin API local | Broker OAuth centralizado |
| Esquemas de manifiesto (`nexus.pack.yaml`, `nexus.blueprint.yaml`, `setup.plan.yaml`) | Orquestación de secretos cifrados a escala |
| SDK y CLI | Monitorización y alertas de flota gestionadas |
| Verificador e instalador de packs | Backups gestionados |
| Cliente de Registry comunitario | Actualizaciones de flota coordinadas |
| Wizard/generador local básico | Catálogo curado y verificado |
| **Seguridad, exportación y portabilidad** | Soporte y SLA; facturación y gestión de cuenta |

## Licencia — PENDIENTE de decisión legal formal

**No es consejo legal.** Ver el trade-off completo en
[ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md):

- **Apache-2.0** (permisiva, todo el proyecto): máxima adopción; riesgo de SaaS competidor sin retorno.
- **AGPL + licencia comercial dual**: protege contra SaaS competidor; posible fricción empresarial.

Debe resolverse con asesoría legal **antes de publicar** el repositorio de Runtime/Operator. No bloquea
el MVP (que no requiere publicar el código todavía). Console es hoy MIT (`LICENSE`).

## Forma de pricing (sin cifras)

| Plan | Para quién | Qué incluye (cualitativo) | Qué dirige el coste |
|---|---|---|---|
| **Community Free** | Desarrolladores, comunidad, self-hosted | Runtime, Operator, CLI, Registry comunitario; sin soporte garantizado | Cero para Ironbat salvo mantenimiento |
| **Managed Starter** | Individuos, freelancers (ruta simple) | Instancia gestionada, cuestionario+blueprint, catálogo curado básico, soporte por ticket/comunidad | Infra de instancia pequeña, bajo volumen LLM |
| **Pro** | Equipos pequeños, profesionales | Multi-usuario, más áreas, actualizaciones de flota, backups gestionados, SLA básico | Volumen LLM, nº usuarios, almacenamiento de memoria |
| **Business/Enterprise** | Organizaciones, verticales | BYOC o infra dedicada, catálogo verificado ampliado, SSO, auditoría avanzada, soporte prioritario | Complejidad de integración, nº usuarios, SLA contractual |

El eje de coste crece con **volumen de LLM, usuarios activos, áreas/packs instalados y nivel de
soporte**, no con funcionalidades básicas de soberanía o seguridad (disponibles en todos los planes).
**Community Free permanece gratuito indefinidamente**; el cobro empieza solo al usar infraestructura
gestionada de Ironbat (decisión #6).
