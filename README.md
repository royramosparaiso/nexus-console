# Nexus Console

**Plano de control de [Nexus OS](https://github.com/royramosparaiso/ironbat-jarvis).**

Nexus Console es el meta-orquestador que despliega y gestiona instancias de Nexus Platform. Se instala **una sola vez** por operador y desde ella se administran N instancias con arquitecturas potencialmente distintas.

> **Impulsado por Ironbat Digital LLC.** Licencia MIT. Todavía en construcción — v0.1 en curso.

## Qué hace

- **Wizard de arquitectura por instancia.** Cuestionario de 6 pasos (persona, modalidad de despliegue, LLMs, memoria/grafos, áreas activas, governance) que emite `nexus.instance.yaml`.
- **Deployer.** Sabe desplegar Nexus Platform a Docker Compose local, Fly.io, Kubernetes u on-prem según la elección del wizard.
- **Instance Registry.** Catálogo persistente de instancias Platform gestionadas.
- **Secret Manager.** Rota y sincroniza credenciales (LLM providers, DB, storage) con cada instancia.
- **Agent Factory.** Crea, edita, versiona y despliega agentes, áreas y coordinadores a las instancias.
- **Jarvis-Console.** Agente propio con el que el operador dialoga en lenguaje natural.

## No hace

- **No gestiona espacios ni usuarios finales.** Eso vive en cada instancia Platform.
- **No accede a datos de negocio de las instancias.** Solo infra + catálogo de agentes.
- **No lee espacios personales.** Ni siquiera con rol `superadmin` de una instancia.

## Arquitectura de referencia

```
                    ┌─────────────────────────┐
                    │    Nexus Console        │  ← este repo
                    │  (control plane)        │
                    └───────────┬─────────────┘
                                │  JWT firmado
                    ┌───────────┼──────────────┐
                    ▼           ▼              ▼
             ┌──────────┐ ┌──────────┐  ┌──────────┐
             │ Platform │ │ Platform │  │ Platform │
             │  local   │ │  Fly.io  │  │   K8s    │
             └──────────┘ └──────────┘  └──────────┘
```

Ver docs de Nexus OS para el modelo completo: [Vision](https://github.com/royramosparaiso/ironbat-jarvis/blob/main/docs/vision.md) · [Specifications](https://github.com/royramosparaiso/ironbat-jarvis/blob/main/docs/specifications.md) · [RFC-001](https://github.com/royramosparaiso/ironbat-jarvis/blob/main/docs/rfc/001-nexus-framework.md).

## Modo local single-tenant

Con un `docker compose up` levantas Console + Postgres + Redis en tu máquina, sin necesidad de tokens cloud. Console detecta que está sola, despliega una Platform local con arquitectura por defecto y crea el `superadmin`.

```bash
git clone https://github.com/royramosparaiso/nexus-console.git
cd nexus-console
docker compose up
```

Console UI: [http://localhost:7000](http://localhost:7000)
Platform UI (auto-desplegada): [http://localhost:7100](http://localhost:7100)

## Stack

- **Backend:** FastAPI (Python 3.12+), SQLAlchemy 2.x, Postgres, Redis, JWT (Ed25519).
- **Frontend:** Vite + React 19 + Tailwind, raw `fetch` (no TanStack Query), dark mode nativo.
- **Deployer:** Docker SDK for Python + adaptadores Fly.io / kubectl / SSH.
- **Contratos:** paquete compartido `nexus-core` (SDK — repo aparte, planeado).

## Roadmap corto

- [ ] Backend `/health`, `/instances` CRUD, `/_platform/notify` stub
- [ ] Admin panel LLM Providers (migrado desde `ironbat-jarvis`)
- [ ] Wizard de arquitectura UI (6 pasos)
- [ ] Deployer para modo local (Docker Compose)
- [ ] Deployer para Fly.io
- [ ] Instance Registry con salud en tiempo real
- [ ] Agent Factory + catalog
- [ ] Jarvis-Console

## Licencia

MIT — ver [LICENSE](LICENSE).
