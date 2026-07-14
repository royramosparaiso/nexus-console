# Hermes — engine selection guide

Hermes is the Nexus kernel orchestrator: agent registry, durable job dispatch,
hot-deploy of new agents, and the pub/sub event bus. It always ships with
every Nexus deployment. What you choose here is only *how* it runs.

There are four engines. Same external API, very different operational
profiles. Pick by matching your constraints — not by capability, because the
capability is identical.

---

## TL;DR

| Constraint                           | Pick                          |
| ------------------------------------ | ----------------------------- |
| Hobby tier, one Postgres already up  | `in_process`                  |
| Standard tier, no ops appetite       | `temporal_cloud`              |
| Standard tier, want to stay self-hosted, already run Postgres | `temporal_selfhost_postgres` |
| Scale tier, managed is fine          | `temporal_cloud`              |
| Scale tier, hard data-residency rule | `temporal_selfhost` (Cassandra) |
| Scale tier, don't want a second datastore | `temporal_selfhost_postgres` |

Everything below expands on that table.

---

## The four engines

### `in_process` — embedded, uses your platform's Postgres

Hermes runs inside the `nexus-platform` process. Durable queue is a table
in the same Postgres your app already uses, plus `LISTEN/NOTIFY` for
low-latency dispatch. No extra infrastructure.

**Choose when:**
- You are on `hobby` or the low end of `standard`.
- You already have Postgres in the stack (you always do).
- You do not need cross-region failover, long-running workflows measured
  in days, or replay debugging.

**Do not choose when:**
- Sustained load exceeds a few thousand jobs/second.
- You need Temporal-style versioned workflow histories, side-effect
  determinism, or workflow replay tools.
- Your operator team already runs Temporal for other systems and wants
  one control plane.

**Cost:** zero incremental. Reuses `DATABASE_URL`.
**Ops:** one migration file, no extra process.
**Recovery:** whatever your Postgres backup story already is.

---

### `temporal_cloud` — managed Temporal (recommended default at scale)

Hermes delegates the durable queue to a Temporal Cloud namespace. You get
managed retries, timeouts, versioned workflows, the UI, metrics, alerts,
and Temporal's SDK ecosystem. Someone else runs the cluster.

**Choose when:**
- You are on `scale`, or on `standard` with real production traffic.
- You want the full Temporal feature set (workflows, activities, signals,
  child workflows, versioning) without operating Cassandra or Postgres.
- Your team is small and cannot afford to page on a Cassandra cluster at
  3 AM.

**Do not choose when:**
- Data residency rules forbid a US/EU managed control plane.
- Budget is tight — Temporal Cloud is not free and the entry price makes
  it wrong for `hobby` (the tier matrix rejects this combination).
- You need to run fully air-gapped.

**Required secrets:** `TEMPORAL_CLOUD_NAMESPACE`, `TEMPORAL_CLOUD_API_KEY`,
`TEMPORAL_CLOUD_ADDRESS`.
**Cost:** billed per action and per active namespace. See
[Temporal Cloud pricing](https://temporal.io/cloud/pricing).
**Ops:** none. You still care about API key rotation and namespace
retention settings.

---

### `temporal_selfhost_postgres` — self-hosted Temporal, Postgres backend

Same Temporal server, running on your infrastructure, using Postgres 16 as
the durable store. Comes with a Web UI on `:8080` and an idempotent
namespace initializer. Bundled compose file:
[`docker-compose.temporal-postgres.yml`](./docker-compose.temporal-postgres.yml).

**Choose when:**
- You want full Temporal semantics but the deployment must stay in your
  own VPC or on-prem.
- Your team already knows Postgres and does not want a second, unfamiliar
  datastore in the ops rotation.
- Expected write throughput is roughly under a few thousand history
  events per second sustained. Postgres scales further than people
  assume, but Cassandra scales further still.
- You are on `standard` and want a self-host path — this is the tier's
  recommended self-host default over Cassandra because the operational
  surface is smaller.

**Do not choose when:**
- You expect very high sustained write throughput and need Cassandra's
  horizontal write scaling. See the Cassandra section below for the
  threshold.
- You cannot afford dedicated Postgres tuning for Temporal's workload
  (long-running history writes, heavy secondary indexes).

**Required secrets:** `TEMPORAL_HOST`, `TEMPORAL_NAMESPACE`,
`TEMPORAL_PG_USER`, `TEMPORAL_PG_PASSWORD`.
**Cost:** the boxes you run it on. Postgres is a single primary here —
add replicas and connection poolers yourself if you need them.
**Ops:** one Postgres instance to backup, monitor and vacuum. Postgres
container binds to `127.0.0.1:5433` externally to avoid clashing with
any other Postgres already on the host.

**Note:** the bundled Postgres is meant for Temporal only. Do not point
your application at it — use the platform's own `DATABASE_URL`.

---

### `temporal_selfhost` — self-hosted Temporal, Cassandra backend

Same Temporal server, Cassandra 4.1 as the durable store. Bundled compose
file: [`docker-compose.temporal.yml`](./docker-compose.temporal.yml).

**Choose when:**
- You expect sustained write throughput that Postgres would struggle
  with. As a rough rule of thumb: consider Cassandra when you plan to
  push more than \~5–10k history events per second sustained, or when
  you already have a Cassandra team.
- You need horizontal write scaling by adding nodes rather than by
  vertical scaling the primary.
- You have Cassandra expertise on the team — repair, compaction and
  cluster health monitoring are not optional.

**Do not choose when:**
- You do not have Cassandra expertise. This is the sharpest edge of the
  four engines. A misconfigured Cassandra cluster will silently corrupt
  Temporal history in ways Postgres will not.
- Your throughput does not actually justify Cassandra. Most Nexus
  installs never come close to needing it.

**Required secrets:** `TEMPORAL_HOST`, `TEMPORAL_NAMESPACE`.
**Cost:** three-node Cassandra is the practical minimum for durability.
Budget accordingly.
**Ops:** Cassandra repair schedule, compaction strategy, JVM heap sizing.
Not a "set and forget" system.

---

## Decision flow

```
Is this hobby tier?
├── Yes → in_process. Done.
└── No
    │
    Do you accept a managed control plane (data leaves your VPC)?
    ├── Yes → temporal_cloud. Done.
    └── No
        │
        Do you have Cassandra expertise on-call AND expect >~5k events/s sustained?
        ├── Yes → temporal_selfhost (Cassandra).
        └── No  → temporal_selfhost_postgres.
```

The wizard enforces the tier matrix so an invalid combination (e.g.
`temporal_cloud` on `hobby`) is rejected up front with an actionable
error.

---

## Migration between engines

Hermes exposes the same external API for all four engines, so agent code
never changes when you migrate. What changes is state:

- `in_process` → any Temporal engine: **not automatic.** Drain in-flight
  jobs from the Postgres tables, cut over, no history is carried.
- Temporal → Temporal (Cloud ↔ selfhost, Postgres ↔ Cassandra): use
  `temporal workflow list` + `temporal workflow reset` or the Temporal
  migration tooling. Namespace name stays the same to keep task queues
  intact.
- Any Temporal → `in_process`: only sensible if load has dropped
  drastically. Not a supported downgrade path — you would be giving up
  workflow histories and versioning.

Plan the migration; do not do it under load.

---

## Where each engine is defined in code

- Engine literal + tier matrix: [`console/app/models/kernel.py`](../../app/models/kernel.py)
- Handoff builders (the shell steps a human or automation runs to bring
  the engine online): [`console/app/services/stack_provisioning.py`](../../app/services/stack_provisioning.py)
- Wizard endpoint (`GET /wizard/kernel?tier=…&engine=…`):
  [`console/app/api/wizard.py`](../../app/api/wizard.py)
- YAML emission: [`console/app/services/wizard_yaml.py`](../../app/services/wizard_yaml.py) —
  writes `spec.stack.kernel.hermes` on every generated `nexus.instance.yaml`.

The Web UI on `:8080` is exposed by both self-host compose files. Bind
address defaults to `127.0.0.1` — override with `TEMPORAL_UI_BIND` if
you need remote access, and put a reverse proxy in front.
