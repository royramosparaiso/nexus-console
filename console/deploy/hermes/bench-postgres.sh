#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# bench-postgres.sh — Run temporalio/maru against the bundled Temporal +
# Postgres compose stack, then extract real STPS numbers.
#
# WHAT IT DOES
#   1. Boots docker-compose.temporal-postgres.yml (or reuses a running one).
#   2. Creates the `benchtest` namespace idempotently.
#   3. Ensures Temporal exposes Prometheus metrics on :8000 so we can read
#      the persistence_requests rate directly from the server (this is the
#      real definition of STPS — anything else is a proxy).
#   4. Boots two workers from the local temporalio/maru clone: the bench
#      worker (runs the benchmark orchestration workflow) and the target
#      worker (runs the workflow being measured).
#   5. Starts a scenario, waits for it to finish, then queries:
#       - maru's own histogram (workflow-level STPS and per-workflow latency)
#       - the Temporal server's persistence metrics (backend-level STPS,
#         which is the number you actually size Cassandra/Postgres against)
#   6. Writes a summary JSON to ./results/ with commit-safe filenames.
#
# WHAT IT INTENTIONALLY DOES NOT DO
#   - Tune Postgres for you. Defaults are single-node dev-grade. See the
#     README benchmarks section — do not quote numbers from this script as
#     production capacity, they're a lower bound.
#   - Deploy to Kubernetes. maru ships a Helm chart, but the whole point
#     here is a single-host reproducible run.
#   - Compare against Cassandra automatically. Re-run with
#     ENGINE=cassandra to point at docker-compose.temporal.yml instead.
#
# USAGE
#   ./bench-postgres.sh                              # basic auto-generated
#                                                    #   scenario, 3000 wfs
#   ./bench-postgres.sh scenarios/spike-ramp.json    # bundled ramp scenario
#                                                    #   5->200/s over 5 steps
#   ./bench-postgres.sh path/to/custom.json          # your own scenario file
#   RATE=100 COUNT=10000 ./bench-postgres.sh         # inline overrides for
#                                                    #   the auto-generated
#                                                    #   scenario
#   ENGINE=cassandra ./bench-postgres.sh             # point at the Cassandra
#                                                    #   compose file instead
#   KEEP_RUNNING=1 ./bench-postgres.sh               # don't tear the stack
#                                                    #   down afterwards
#
# DEPENDENCIES
#   - docker + docker compose v2
#   - temporal CLI on PATH (the modern replacement for tctl:
#     https://docs.temporal.io/cli). tctl is also accepted as a fallback.
#   - git, jq, curl, awk, python3
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ───── config ────────────────────────────────────────────────────────────────

ENGINE="${ENGINE:-postgres}"        # postgres | cassandra
SCENARIO="${1:-}"                    # optional path to a maru scenario JSON.
                                     # Resolved relative to $HERE if the path
                                     # doesn't exist as given (so
                                     # 'scenarios/spike-ramp.json' works from
                                     # anywhere).
RATE="${RATE:-20}"                   # workflows/sec target when auto-generating
COUNT="${COUNT:-3000}"               # total workflows when auto-generating
ACTIVITIES="${ACTIVITIES:-3}"        # sequenceCount for the target workflow
CONCURRENCY="${CONCURRENCY:-5}"      # driver concurrency
TIMEOUT_S="${TIMEOUT_S:-1800}"       # bench workflow execution timeout

NAMESPACE="benchtest"
BENCH_TASK_QUEUE="temporal-bench"
TARGET_TASK_QUEUE="temporal-basic"
BENCH_WORKFLOW_ID="bench-$(date +%s)"

HERE="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="${HERE}/results"
MARU_DIR="${MARU_DIR:-${HERE}/.maru}"

case "$ENGINE" in
    postgres)  COMPOSE_FILE="${HERE}/docker-compose.temporal-postgres.yml" ;;
    cassandra) COMPOSE_FILE="${HERE}/docker-compose.temporal.yml" ;;
    *) echo "ERROR: ENGINE must be 'postgres' or 'cassandra' (got: $ENGINE)" >&2; exit 2 ;;
esac

TEMPORAL_ADDR="${TEMPORAL_ADDR:-127.0.0.1:7233}"
METRICS_URL="${METRICS_URL:-http://127.0.0.1:8000/metrics}"

# ───── prerequisites ─────────────────────────────────────────────────────────

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' not on PATH" >&2; exit 2; }; }
need docker
need git
need jq
need curl
need awk
need python3

# Prefer the modern `temporal` CLI. tctl still works but is deprecated.
if command -v temporal >/dev/null 2>&1; then
    TEMPORAL_CLI="temporal"
elif command -v tctl >/dev/null 2>&1; then
    TEMPORAL_CLI="tctl"
else
    echo "ERROR: neither 'temporal' nor 'tctl' on PATH." >&2
    echo "Install: https://docs.temporal.io/cli" >&2
    exit 2
fi

mkdir -p "$RESULTS_DIR"

echo "==> Engine:              $ENGINE"
echo "==> Compose file:        $COMPOSE_FILE"
echo "==> Temporal address:    $TEMPORAL_ADDR"
echo "==> Metrics endpoint:    $METRICS_URL"
echo "==> Results dir:         $RESULTS_DIR"
echo "==> Bench workflow id:   $BENCH_WORKFLOW_ID"

# ───── 1. boot the compose stack (or reuse it) ───────────────────────────────

if docker compose -f "$COMPOSE_FILE" ps --status running 2>/dev/null | grep -q temporal; then
    echo "==> Compose stack already running, reusing."
else
    echo "==> Bringing up compose stack..."
    docker compose -f "$COMPOSE_FILE" up -d
fi

echo "==> Waiting for Temporal frontend to be reachable at $TEMPORAL_ADDR..."
for i in $(seq 1 60); do
    if $TEMPORAL_CLI operator cluster health --address "$TEMPORAL_ADDR" >/dev/null 2>&1; then
        break
    fi
    sleep 2
    if [ "$i" -eq 60 ]; then
        echo "ERROR: Temporal frontend did not come up within 120s." >&2
        docker compose -f "$COMPOSE_FILE" logs --tail=50 temporal >&2 || true
        exit 3
    fi
done

# ───── 2. namespace ──────────────────────────────────────────────────────────

echo "==> Ensuring namespace '$NAMESPACE' exists..."
$TEMPORAL_CLI operator namespace create \
    --address "$TEMPORAL_ADDR" \
    --namespace "$NAMESPACE" \
    --retention 1d 2>/dev/null || true

# ───── 3. metrics endpoint sanity check ──────────────────────────────────────
# The bundled compose file does not enable Prometheus by default. If you see
# this warning, add `PROMETHEUS_ENDPOINT: 0.0.0.0:8000` to the temporal
# service's environment in the compose file and restart it.

if ! curl -fsS -m 3 "$METRICS_URL" >/dev/null 2>&1; then
    echo "WARNING: Prometheus metrics endpoint $METRICS_URL is not reachable."
    echo "         Backend-level STPS will not be measured. To enable, set"
    echo "         PROMETHEUS_ENDPOINT=0.0.0.0:8000 in the compose file's"
    echo "         'x-temporal-env' block and re-run."
    HAVE_METRICS=0
else
    HAVE_METRICS=1
fi

# ───── 4. maru workers ───────────────────────────────────────────────────────

if [ ! -d "$MARU_DIR" ]; then
    echo "==> Cloning temporalio/maru into $MARU_DIR..."
    git clone --depth 1 https://github.com/temporalio/maru.git "$MARU_DIR"
fi

echo "==> Building maru workers (docker image)..."
docker build -q -t nexus-maru:local "$MARU_DIR" >/dev/null

# The compose stack runs on host network binds, so the worker connects via
# the host loopback. FRONTEND_ADDRESS is the standard maru env var.
docker rm -f nexus-maru-bench nexus-maru-target >/dev/null 2>&1 || true

echo "==> Starting bench worker (task queue: $BENCH_TASK_QUEUE)..."
docker run -d --name nexus-maru-bench \
    --network host \
    -e FRONTEND_ADDRESS="$TEMPORAL_ADDR" \
    -e TEMPORAL_NAMESPACE="$NAMESPACE" \
    -e BENCH_WORKER=true \
    nexus-maru:local >/dev/null

echo "==> Starting target worker (task queue: $TARGET_TASK_QUEUE)..."
docker run -d --name nexus-maru-target \
    --network host \
    -e FRONTEND_ADDRESS="$TEMPORAL_ADDR" \
    -e TEMPORAL_NAMESPACE="$NAMESPACE" \
    -e BASIC_WORKER=true \
    nexus-maru:local >/dev/null

# Give workers a few seconds to poll and register with Temporal.
sleep 5

# ───── 5. scenario ───────────────────────────────────────────────────────────

if [ -n "$SCENARIO" ] && [ ! -f "$SCENARIO" ] && [ -f "${HERE}/${SCENARIO}" ]; then
    SCENARIO="${HERE}/${SCENARIO}"
fi

if [ -z "$SCENARIO" ]; then
    SCENARIO="${RESULTS_DIR}/scenario-${BENCH_WORKFLOW_ID}.json"
    echo "==> Generating scenario: rate=${RATE}/s, count=${COUNT}, activities=${ACTIVITIES}"
    cat > "$SCENARIO" <<JSON
{
    "steps": [{
        "count": ${COUNT},
        "ratePerSecond": ${RATE},
        "concurrency": ${CONCURRENCY}
    }],
    "workflow": {
        "name": "basic-workflow",
        "taskQueue": "${TARGET_TASK_QUEUE}",
        "args": {
            "sequenceCount": ${ACTIVITIES},
            "parallelCount": 1
        }
    },
    "report": {
        "intervalInSeconds": 10
    }
}
JSON
fi

echo "==> Using scenario: $SCENARIO"

# ───── 6. baseline metrics snapshot (if available) ───────────────────────────

metric_value() {
    # Sum a Prometheus counter, filter by operation regex.
    # Returns 0 if the metric or endpoint is missing — never fails.
    local op_regex="$1"
    curl -fsS -m 5 "$METRICS_URL" 2>/dev/null | \
        awk -v re="$op_regex" '
            /^persistence_requests/ && $0 ~ re {
                # Extract the numeric value (last space-separated field).
                v = $NF; sum += v
            }
            END { printf "%.0f", sum + 0 }
        '
}

if [ "$HAVE_METRICS" = "1" ]; then
    BASELINE_TS=$(date +%s)
    BASELINE_WRITES=$(metric_value 'CreateWorkflowExecution|UpdateWorkflowExecution|AppendHistoryNodes')
    echo "==> Baseline persistence write counter: $BASELINE_WRITES"
else
    BASELINE_TS=$(date +%s)
    BASELINE_WRITES=0
fi

# ───── 7. start the bench workflow ───────────────────────────────────────────

echo "==> Starting maru bench workflow..."
$TEMPORAL_CLI workflow start \
    --address "$TEMPORAL_ADDR" \
    --namespace "$NAMESPACE" \
    --task-queue "$BENCH_TASK_QUEUE" \
    --type bench-workflow \
    --workflow-id "$BENCH_WORKFLOW_ID" \
    --execution-timeout "${TIMEOUT_S}s" \
    --task-timeout 5s \
    --input-file "$SCENARIO"

echo "==> Waiting for bench workflow to complete (timeout: ${TIMEOUT_S}s)..."
$TEMPORAL_CLI workflow result \
    --address "$TEMPORAL_ADDR" \
    --namespace "$NAMESPACE" \
    --workflow-id "$BENCH_WORKFLOW_ID" \
    > "${RESULTS_DIR}/${BENCH_WORKFLOW_ID}-result.json" || {
        echo "ERROR: bench workflow did not complete cleanly." >&2
        echo "       See Temporal UI at http://127.0.0.1:8080 for details." >&2
        exit 4
    }

# ───── 8. extract results ────────────────────────────────────────────────────

echo "==> Querying maru histogram..."
$TEMPORAL_CLI workflow query \
    --address "$TEMPORAL_ADDR" \
    --namespace "$NAMESPACE" \
    --workflow-id "$BENCH_WORKFLOW_ID" \
    --type histogram_csv \
    > "${RESULTS_DIR}/${BENCH_WORKFLOW_ID}-histogram.csv" || true

if [ "$HAVE_METRICS" = "1" ]; then
    FINAL_TS=$(date +%s)
    FINAL_WRITES=$(metric_value 'CreateWorkflowExecution|UpdateWorkflowExecution|AppendHistoryNodes')
    ELAPSED=$(( FINAL_TS - BASELINE_TS ))
    if [ "$ELAPSED" -gt 0 ]; then
        DELTA=$(( FINAL_WRITES - BASELINE_WRITES ))
        STPS=$(python3 -c "print(f'{${DELTA}/${ELAPSED}:.1f}')")
    else
        STPS="0.0"
    fi
else
    ELAPSED=0
    DELTA=0
    STPS="unknown (metrics endpoint disabled)"
fi

# maru histogram_csv row format: bucket_start,bucket_end,started,closed
# We derive wall-clock throughput from the closed column.
WORKFLOWS_PER_S=$(awk -F, '
    NR > 1 && $4 != "" {
        total_closed += $4
        buckets++
    }
    END {
        if (buckets > 0 && total_closed > 0) {
            # Each bucket is intervalInSeconds wide (default 10s).
            printf "%.2f", total_closed / (buckets * 10)
        } else {
            printf "0.00"
        }
    }
' "${RESULTS_DIR}/${BENCH_WORKFLOW_ID}-histogram.csv" 2>/dev/null || echo "0.00")

# ───── 9. summary ────────────────────────────────────────────────────────────

SUMMARY="${RESULTS_DIR}/${BENCH_WORKFLOW_ID}-summary.json"
python3 - <<PY > "$SUMMARY"
import json, os, subprocess

engine = "${ENGINE}"
compose = "${COMPOSE_FILE}"

# Grab container image digests for reproducibility.
def image(svc):
    try:
        cid = subprocess.check_output(
            ["docker", "compose", "-f", compose, "ps", "-q", svc],
            text=True,
        ).strip().splitlines()[0]
        return subprocess.check_output(
            ["docker", "inspect", "--format", "{{.Config.Image}}", cid],
            text=True,
        ).strip()
    except Exception:
        return None

summary = {
    "run_id": "${BENCH_WORKFLOW_ID}",
    "engine": engine,
    "scenario": "${SCENARIO}",
    "images": {
        "temporal": image("temporal"),
        "backend":  image("postgres" if engine == "postgres" else "cassandra"),
    },
    "config": {
        "target_workflows_per_sec": ${RATE},
        "total_workflows":          ${COUNT},
        "activities_per_workflow":  ${ACTIVITIES},
        "concurrency":              ${CONCURRENCY},
    },
    "results": {
        "workflows_per_sec_observed": float("${WORKFLOWS_PER_S}"),
        "backend_stps":               "${STPS}",
        "backend_writes_delta":       ${DELTA},
        "wall_clock_seconds":         ${ELAPSED},
        "have_backend_metrics":       bool(${HAVE_METRICS}),
    },
    "notes": [
        "workflows_per_sec_observed is closed workflows / wall clock,",
        "derived from maru's histogram_csv.",
        "backend_stps is persistence_requests delta / wall clock,",
        "which is the number to size the backend against.",
        "If have_backend_metrics=false, enable PROMETHEUS_ENDPOINT in the",
        "compose file and re-run for a real STPS number.",
    ],
}
print(json.dumps(summary, indent=2))
PY

echo
echo "──────────────────────────────────────────────────────────────────────"
echo " Results"
echo "──────────────────────────────────────────────────────────────────────"
cat "$SUMMARY"
echo
echo " Detailed histogram: ${RESULTS_DIR}/${BENCH_WORKFLOW_ID}-histogram.csv"
echo " Summary:            ${SUMMARY}"
echo

# ───── 10. teardown ──────────────────────────────────────────────────────────

if [ "${KEEP_RUNNING:-0}" != "1" ]; then
    echo "==> Tearing down maru workers (KEEP_RUNNING=1 to skip)..."
    docker rm -f nexus-maru-bench nexus-maru-target >/dev/null 2>&1 || true
    echo "==> Stopping compose stack..."
    docker compose -f "$COMPOSE_FILE" down
else
    echo "==> KEEP_RUNNING=1 — stack left up."
    echo "    UI:      http://127.0.0.1:8080"
    echo "    Metrics: $METRICS_URL"
    echo "    Tear down: docker compose -f $COMPOSE_FILE down"
fi
