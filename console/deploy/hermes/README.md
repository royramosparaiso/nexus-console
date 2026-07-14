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
- Expected sustained load is roughly **under ~300 STPS** (see the
  benchmarks section below for the reasoning). Postgres carries further
  than people assume with tuning, but Cassandra scales further still.
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
- You expect sustained load that Postgres would struggle with. As a
  rough rule of thumb (see benchmarks section): **consider Cassandra
  above roughly ~300 STPS sustained**, or when you already have a
  Cassandra team.
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
        Do you have Cassandra expertise on-call AND expect >~300 STPS sustained?
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

## Real-world benchmarks

The fastest way to lie about Temporal capacity is to quote someone else's
STPS number. Persistence throughput depends on backend size, RF, JVM/PG
tuning, shard count, history size per workflow, and how chatty your
activities are. Numbers below are anchored to specific public sources —
read the source before using any of them as a sizing input.

### The right unit

Temporal measures itself in **state transitions per second (STPS)** —
every persistence write. It is not the same as workflows/sec or
activities/sec: a 3-activity workflow is roughly 8–12 state transitions.
Most public numbers report either STPS or actions/sec (APS) — do not
compare them directly, and translate to STPS before sizing.

See [Temporal — Scaling Temporal: The basics](https://temporal.io/blog/scaling-temporal-the-basics)
for the definition and the reference dev-default run (150 → 1,350
STPS by tuning shards, replicas, and DB size — Cassandra backend).

### Rule-of-thumb per vCPU (Cassandra)

From a Temporal core-team answer on the community forum
([source](https://community.temporal.io/t/temporal-throughput/2263)):

- **~60 STPS per Cassandra vCPU**, at RF=3.
- **~150 STPS per Temporal-cluster vCPU** (frontend + history + matching).

So a 3-node Cassandra cluster of 8 vCPU each (~24 vCPU total) is
nominally good for ~1,400 STPS before you start tuning. Reality is
lower once you add history-event size and secondary indexes, but the
ratio is a useful sanity check when the backend is the bottleneck.

### Postgres ceilings observed in production reports

All from public sources — take each as one datapoint, not a spec.

| Setup                                                              | Sustained throughput                                    | Source                                                                                                                                                                       |
| ------------------------------------------------------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Single Postgres 12, 2 vCPU / 8 GB, 1 activity/wf                   | ~8–10 workflows/s (~40–50 activities/s), DB pegged 100% | [Temporal forum](https://community.temporal.io/t/running-temporal-postgres-benchmark/836)                                                                                    |
| Same setup, DB scaled to 4 vCPU / 16 GB                            | ~16 workflows/s, DB at 80%                              | [Temporal forum](https://community.temporal.io/t/running-temporal-postgres-benchmark/836)                                                                                    |
| Single Postgres, 8-core SSD, 3-activity REST-call workflow         | Target 500 TPS not reached — latency degraded past ~10 req/s | [Temporal forum](https://community.temporal.io/t/navigating-through-the-internal-of-workflow-lifecycle/11567)                                                                |
| Managed Postgres, tuned services, 3-activity workflow              | ~75 workflows/s, ~230 activities/s, DB at 40–50% CPU    | [Temporal forum](https://community.temporal.io/t/postgresql-specification-for-temporal/6902)                                                                                 |
| Postgres 60k bursty workflows / 15 min question (community advice) | Community consensus: ~50–200 workflow starts/s ceiling on Postgres | [Temporal forum](https://community.temporal.io/t/can-temporal-postgres-handle-60k-bursty-scheduled-workflows-every-15-minutes/19420)                                         |

Collectively: **a single well-tuned Postgres, sensibly sized, gets
you to roughly the 50–200 workflows/s / a few hundred activities/s
range**. Beyond that you are fighting `pg_locks`, autovacuum, and the
`history_node` hot table — as the Quo team documented before migrating
away ([Outgrowing Postgres and Moving to Cassandra](https://www.quo.com/blog/postgres-to-cassandra/)).

### When Cassandra pays off

Same Quo write-up above, plus the Temporal core team's public guidance
(["we recommend Cassandra for huge loads"](https://community.temporal.io/t/postgresql-good-option-for-persistence-in-production/6153)):

- Cassandra is Temporal's **reference backend** — it is what the core
  team benchmarks and tunes against.
- It is **sharded and write-optimized by design**. Adding a node adds
  throughput; adding a Postgres replica does not (writes still go
  through the primary).
- Quo sustained "roughly 3× peak production state-transition rate"
  on a 3-node Cassandra cluster at RF=3 with 32 matching partitions —
  a comfortable margin for their workload. The engineering effort to
  get there was non-trivial (RF tuning, matching partition scaling,
  monitoring).
- Public case study of a self-hosted migration: 100% CPU on Postgres →
  ~3× cheaper and ~3–4× faster on 3-node Cassandra
  ([Temporal Replay talk 2026](https://www.youtube.com/watch?v=H1wkzi_bdTU)).
  The speaker also notes that Astra DB (managed Cassandra) was much
  more expensive than their self-hosted alternative — factor that into
  the total cost.

### Temporal Cloud reference points

- Default namespace limit: **500 actions per second (APS)**, floor that
  scales up with On-Demand Capacity based on the last 7 days of usage.
  Higher tiers via Provisioned Capacity.
  ([Temporal Cloud limits](https://docs.temporal.io/cloud/limits))
- Temporal's own claim is that Cloud has **lower and more stable
  request latency than most self-hosted clusters** because of a
  custom persistence layer, not stock Cassandra
  ([Temporal Cloud custom persistence layer](https://temporal.io/blog/higher-throughput-and-lower-latency-temporal-clouds-custom-persistence-layer)).
  Treat this as vendor claim; still, the practical implication is that
  "beat Cloud on latency with self-hosted" is not a free win.

### Practical sizing shortcut

1. Estimate your **peak STPS**: expected workflows/s × average state
   transitions per workflow (start + one per activity + completion, plus
   any signals/timers). A typical 3-activity workflow ≈ 8–12 STPS.
2. **If peak STPS ≲ 500** and you can accept a managed vendor →
   `temporal_cloud` at default APS is a fit. Below the default floor
   you pay for headroom you may not use, but the ops savings are real.
3. **If peak STPS ≲ 300 and you want self-host** →
   `temporal_selfhost_postgres` with a well-tuned Postgres (SSD, tuned
   `shared_buffers`, autovacuum-friendly settings, connection pooler).
   Multiple community reports land in this band before Postgres becomes
   the bottleneck.
4. **If peak STPS is roughly 300–2,000 and self-host is a hard
   requirement** → `temporal_selfhost` (Cassandra), 3 nodes minimum,
   RF=3. Expect real ops work.
5. **If peak STPS > 2,000 sustained** → Cassandra is table stakes, and
   you should also be reading the Temporal scaling posts end-to-end,
   sizing history shards up-front, and planning for OpenSearch as
   the visibility store.

These boundaries are approximate. **Test with
[maru](https://github.com/temporalio/maru) or the
[temporalio/benchmark-workers](https://github.com/temporalio/benchmark-matrix)
rig against a cluster shaped like your real workload before
committing to a backend at scale.** Every number above should be
treated as a rough anchor, not a spec sheet — see the linked sources
for exact hardware, tuning, and workload shape.

---

## Reproducing these numbers yourself

The [`bench-postgres.sh`](./bench-postgres.sh) script in this directory
runs [temporalio/maru](https://github.com/temporalio/maru) against the
bundled Postgres compose stack and extracts two metrics:

- `workflows_per_sec_observed` — closed workflows / wall clock, from
  maru's own `histogram_csv` query.
- `backend_stps` — delta of the Temporal server's `persistence_requests`
  counter (scraped from `:8000/metrics`) divided by wall clock. This is
  the real STPS number to size the backend against.

Usage:

```bash
# default: 3000 workflows at 20/s, 3 activities each, on the Postgres stack
./bench-postgres.sh

# push harder
RATE=100 COUNT=10000 ACTIVITIES=5 ./bench-postgres.sh

# same stack, but point maru at the Cassandra compose instead
ENGINE=cassandra ./bench-postgres.sh

# keep the stack up so you can inspect the UI at http://127.0.0.1:8080
KEEP_RUNNING=1 ./bench-postgres.sh
```

Results land in `./results/<run-id>-summary.json` next to the raw
histogram CSV. The script uses the modern `temporal` CLI
([docs.temporal.io/cli](https://docs.temporal.io/cli)); `tctl` also
works as a fallback.

**Caveat:** the bundled compose files are single-node dev-grade. Numbers
from this script are a *lower bound* for what a tuned production
cluster does — they are useful for A/B comparing engines on identical
hardware, not for capacity planning against real production traffic.

---

## Monthly cost estimates

All figures are **rough anchors**, dated **July 2026**. Every real
deployment differs; use these to compare engines on identical assumptions,
not as a quote. Sources for every number are linked below the tables.

**Assumed workload sizes per tier** (roughly aligned with `HERMES_ENGINES_BY_TIER`):

| Tier       | Peak STPS | Sustained STPS | Actions/month (Cloud equivalent)¹ |
| ---------- | --------- | -------------- | ---------------------------------- |
| `hobby`    | ~5        | ~1             | ~2.6 M                             |
| `standard` | ~50       | ~15            | ~40 M                              |
| `scale`    | ~500      | ~150           | ~400 M                             |

¹ STPS ≠ Actions 1:1. State transitions are persistence writes; Actions
are the billing unit Temporal Cloud defines
([Cloud Actions](https://docs.temporal.io/cloud/actions)). Assumed here:
monthly Actions ≈ sustained STPS × 3600 × 24 × 30 rounded to a
deploy-friendly bucket. Your ratio may differ — use the estimator in
[docs.temporal.io/cloud/migrate/estimate-actions](https://docs.temporal.io/cloud/migrate/estimate-actions).

### `hobby` tier

| Engine                       | Compute (cloud VMs)               | Backend    | Managed fees | Estimated monthly (USD)          |
| ---------------------------- | --------------------------------- | ---------- | ------------ | -------------------------------- |
| `in_process`                 | Reuses platform Postgres + app VM | —          | —            | **$0 incremental**               |
| `temporal_cloud`             | —                                 | —          | Not allowed on hobby tier | —                   |
| `temporal_selfhost_postgres` | Not allowed on hobby tier         | —          | —            | —                                |
| `temporal_selfhost`          | Not allowed on hobby tier         | —          | —            | —                                |

On hobby the only engine allowed is `in_process`. Cost is dominated by
the app VM you would run anyway.

### `standard` tier (assume ~40 M actions/month, ~15 STPS sustained)

| Engine                       | Compute (cloud VMs)                                   | Backend                                | Managed fees                     | Estimated monthly (USD)  |
| ---------------------------- | ----------------------------------------------------- | -------------------------------------- | -------------------------------- | ------------------------ |
| `in_process`                 | +0 (rides the app VMs)                                | Reuses `DATABASE_URL`                  | —                                | **~$0 incremental**      |
| `temporal_cloud`             | —                                                     | —                                      | Essentials $100 + 39 M × ladder²  | **~$1,640 / mo**         |
| `temporal_selfhost_postgres` | 2 × small VMs (Temporal + workers) ≈ $80              | Managed Postgres, ~4 vCPU / 16 GB ≈ $200 | —                              | **~$280 / mo**           |
| `temporal_selfhost`          | 2 × small VMs ≈ $80 + 3-node Cassandra: overkill here | 3 × 4 vCPU nodes ≈ $450                 | —                                | **~$530 / mo (overkill)** |

² Essentials plan: $100/mo base, includes 1 M Actions; overage at $50 per
million for the next 5 M. 40 M actions/month lands squarely in the
volume-discount ladder — the arithmetic is $100 + (5 M × $50) +
(5 M × $45) + (10 M × $40) + (19 M × $35) = **$1,640**.

At standard, **`temporal_selfhost_postgres` is the price-performance
sweet spot** — roughly 6× cheaper than Cloud at this volume. Cassandra
self-host does not pay off yet.

### `scale` tier (assume ~400 M actions/month, ~150 STPS sustained)

| Engine                       | Compute (cloud VMs)                                                                                       | Backend                                                | Managed fees                         | Estimated monthly (USD)         |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------ | ------------------------------- |
| `in_process`                 | Not realistic at 150 STPS — blocked by design (matrix keeps it last)                                       | —                                                      | —                                    | —                               |
| `temporal_cloud`             | —                                                                                                         | —                                                      | Business $500 + 397.5 M × volume rate³ | **~$11,400 / mo**             |
| `temporal_selfhost_postgres` | 3 × medium VMs (Temporal frontend/history/matching) ≈ $450                                                 | Managed Postgres, ~8 vCPU / 32 GB w/ replicas ≈ $800    | —                                    | **~$1,250 / mo (tight fit)**    |
| `temporal_selfhost`          | 3 × medium VMs ≈ $450                                                                                     | 3-node Cassandra, ~8 vCPU each ≈ $900 + OpenSearch ≈ $250 | —                                  | **~$1,600 / mo**                |

³ Business plan: $500/mo base, 2.5 M included Actions, volume ladder
starting at $50/M for the first 5 M then dropping to $25/M above 200 M.
Arithmetic: $500 + (5 M × $50) + (5 M × $45) + (10 M × $40) + (30 M × $35) +
(50 M × $30) + (100 M × $25) + (197.5 M × $25) = **$11,362**. Rounded to $11,400.

At scale, **`temporal_selfhost` (Cassandra) becomes the cost floor** —
but only when you can actually operate it. Postgres self-host is
cheaper on paper at ~150 STPS but with no headroom above ~300 STPS
(see benchmark table above). Cloud costs ~10× more than self-host at
this volume (~9×), and the price of that ratio is the SRE labor you save.

### Cost-model caveats

- **VM prices** are approximations for AWS `t3.medium` / `m6i.large`
  and RDS `db.m6g.large` sizes in `us-east-1`, on-demand, July 2026.
  Substitute your provider's list price.
- **Egress, backups, snapshots, and OpenSearch** are excluded except
  where noted. Real bills add 10–30% for those depending on retention
  policy.
- **SRE labor is the invisible line item.** Cassandra self-host adds
  the equivalent of a fractional SRE headcount — material for a small
  team, invisible for a platform team already running Cassandra.
- **Egress from Temporal Cloud** is a common surprise: workers stream
  workflow histories back to your VPC. Budget it explicitly.
- **Storage costs** on Temporal Cloud are separate: Active $0.042/GBh,
  Retained $0.00105/GBh
  ([Cloud pricing](https://docs.temporal.io/cloud/pricing)). At 400 M
  actions/month with modest history sizes this is small compared to
  Action pricing, but big long-running workflows can flip the ratio.

### Cost sources

- Temporal Cloud plan tiers, base fees and Action ladder:
  [temporal.io/pricing](https://temporal.io/pricing) and
  [docs.temporal.io/cloud/pricing](https://docs.temporal.io/cloud/pricing).
- Startup credits ($6,000 free) via the Temporal for Startups program —
  factor in if applicable.
- 2024 pricing update context (Actions floor rose from $25/M to $50/M,
  effective Feb 2025 for existing customers):
  [temporal.io/blog/temporal-cloud-pricing-update](https://temporal.io/blog/temporal-cloud-pricing-update).
- Managed Cassandra cost anecdote (Astra DB "very expensive" vs 3-node
  self-host being ~3× cheaper): [Temporal Replay 2026 talk](https://www.youtube.com/watch?v=H1wkzi_bdTU).

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
