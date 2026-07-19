# Especificaciones de NexusOS: Personal + Hub (`v1alpha2`)

Especificaciones detalladas, **listas para implementar**, de la capa de producto Personal + Hub. Todas
son **TARGET-STATE**: describen el estado objetivo, no código existente. Extienden la
[arquitectura del Portal Gestionado (`v1alpha1`)](../architecture/managed-platform-architecture.md) de
forma aditiva.

Cada especificación sigue una estructura consistente: problema/contexto, objetivos, no-objetivos,
actores, conceptos/modelo de datos, requisitos funcionales (P0/P1/P2), flujos y transiciones de estado,
fronteras de API/contrato, seguridad/privacidad, comportamiento ante fallo/offline, telemetría/
observabilidad, criterios de aceptación (Given/When/Then), métricas de éxito, dependencias,
migración/versionado y preguntas abiertas.

| # | Especificación | Alcance |
|---|---|---|
| a | [Personal Runtime](a-personal-runtime.md) | Edición Personal libre, un propietario, sin Hub. |
| b | [Nexus Hub](b-nexus-hub.md) | Plano de control hospedado: cuentas, entitlements, catálogo. |
| c | [Team / Organization](c-team-organization.md) | Multiusuario, roles, políticas de organización. |
| d | [Operator y ciclo de vida de instancia](d-operator-instance-lifecycle.md) | Enrolamiento, reconciliación, salud. |
| e | [Registry / Catálogo y distribución](e-registry-catalog-distribution.md) | Cuatro carriles, mirrors, grants. |
| f | [Modelo de paquetes y artefactos](f-package-artifact-model.md) | Agentes, skills, flows, sidecars, skulls, tareas programadas. |
| g | [Entitlements, suscripciones y degradación](g-entitlements-subscriptions-degradation.md) | Verificación offline, ciclo de vida. |
| h | [Seguridad, confianza, firma y secretos](h-security-trust-signing-secrets.md) | Ed25519, Cosign, minisign, age/X25519, mTLS. |
| i | [Studio: autoría y publicación](i-studio-authoring-publishing.md) | Creación verificada, overlays, publicación. |
| j | [Modalidades de despliegue](j-deployment-modalities.md) | self-hosted / BYOC / managed, ortogonal a edición. |

**Contratos relacionados:** [`docs/schemas/v1alpha2/`](../schemas/v1alpha2/). **Validación:**
`console/tests/test_managed_platform_schemas.py`.
