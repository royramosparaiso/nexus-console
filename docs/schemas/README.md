# Esquemas del Portal Gestionado (`v1alpha1`)

Esquemas **JSON Schema 2020-12** que definen los contratos machine-readable del portal gestionado de
NexusOS. **TARGET-STATE:** ningún componente que los consume (Hub, Operator, Registry) está
implementado; estos esquemas fijan la forma acordada **antes** de escribir código.

## Versionado

- Directorio de versión: [`v1alpha1/`](v1alpha1/). Cada esquema lleva `x-nexus-contract-version:
  "v1alpha1"` y un `$id` estable bajo `https://schemas.nexusos.dev/v1alpha1/`.
- La versión de contrato es **independiente** de la versión del paquete `nexus-console`
  (ver [nota de versionado](../architecture/migration-and-compatibility.md#versionado)).
- Convención de estilo: envoltorio `apiVersion: nexus.io/v1alpha1`, `kind`, `metadata`, `spec`
  (coherente con el `nexus.instance.yaml` que emite el wizard actual). `additionalProperties: false`
  donde la forma es cerrada; `enum`/`pattern`/`minimum` donde aplica; `$id`, `title` y `description`
  en todos.

## Esquemas

| Esquema | Contrato | Notas |
|---|---|---|
| [`common.defs.schema.json`](v1alpha1/common.defs.schema.json) | Definiciones compartidas | `SemVer`, `Slug`, `InstanceId`, `Signature`, `ReplayGuard`, enums |
| [`nexus.blueprint.schema.json`](v1alpha1/nexus.blueprint.schema.json) | `nexus.blueprint.yaml` | Arquitectura recomendada, versionada; sin secretos |
| [`setup.plan.schema.json`](v1alpha1/setup.plan.schema.json) | `setup.plan.yaml` | Plan ordenado de tareas |
| [`setup.task.schema.json`](v1alpha1/setup.task.schema.json) | `SetupTask` | Máquina de estados; `failure_reason` obligatorio si `failed` |
| [`nexus.pack.schema.json`](v1alpha1/nexus.pack.schema.json) | `nexus.pack.yaml` | Pack firmado; `tests` y `uninstall` obligatorios |
| [`desired-state.schema.json`](v1alpha1/desired-state.schema.json) | Estado deseado | Envoltorio firmado + replay guard; intents acotados, sin shell |
| [`enrollment.request.schema.json`](v1alpha1/enrollment.request.schema.json) | Enrolamiento (petición) | Token de un solo uso + clave pública de instancia |
| [`enrollment.response.schema.json`](v1alpha1/enrollment.response.schema.json) | Enrolamiento (respuesta) | Credencial de vida corta + clave pública del Hub |
| [`status-report.schema.json`](v1alpha1/status-report.schema.json) | Status/health | Metadatos de flota y salud; nunca contenido |
| [`secrets-bundle-manifest.schema.json`](v1alpha1/secrets-bundle-manifest.schema.json) | Manifiesto público del bundle | **Solo metadatos**; prohíbe valores de secreto por construcción |

## Ejemplos (fixtures)

En [`examples/`](examples/), con [`examples/index.json`](examples/index.json) mapeando cada fixture a
su esquema. Cubren Managed (real-estate Madrid/Marbella), BYOC, self-hosted/offline, un pack vertical,
plan de setup, estado deseado, enrolamiento, status-report y manifiesto de secrets bundle.

## Validación

`console/tests/test_managed_platform_schemas.py` valida que (1) cada esquema es JSON Schema 2020-12
válido, (2) cada ejemplo valida contra su esquema, (3) ningún ejemplo filtra secretos en texto plano,
y (4) los enlaces relativos de la documentación resuelven. Se ejecuta con el `pytest` existente:

```bash
pip install -e "./console[dev]"
cd console && pytest tests/test_managed_platform_schemas.py -q
```
