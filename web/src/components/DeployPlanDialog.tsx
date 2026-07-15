import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Check,
  RotateCcw,
  Rocket,
  Sparkles,
  X,
} from "lucide-react";
import { apiFetch } from "../lib/api";
import { useOptionalToast } from "./Toast";
import {
  acceptAllRecommendations,
  groupByArea,
  reconcilePlan,
  resetToRecommendation,
  setAreaManually,
  unassignedCount,
  type AreaOption,
  type PlanEntry,
  type RecommendResponse,
  type RecommendationSource,
} from "../lib/areaPlan";

// Minimal shape needed from a catalogue card.
export interface DeployCard {
  id: string;
  artifact_type: "agent" | "sidecar" | "skill";
}

interface Instance {
  instance_id: string;
  name: string;
  persona_display_name: string;
  modality: string;
  version: string | null;
  status: string;
}

interface CommandAccepted {
  accepted: boolean;
  cmd_id: string;
  status: string;
  detail: string | null;
}

type CommandStatus =
  | "queued"
  | "in_progress"
  | "applied"
  | "failed"
  | "rejected";

interface CommandLog {
  cmd_id: string;
  instance_id: string;
  kind: string;
  status: CommandStatus;
  detail: string | null;
  error_code: string | null;
}

const TERMINAL: CommandStatus[] = ["applied", "failed", "rejected"];

const DRAFT_PREFIX = "nexus:deploy-plan:";

const SOURCE_LABEL: Record<RecommendationSource, string> = {
  template_default: "template default",
  tag_match: "capability match",
  domain_match: "domain match",
  fallback: "no match",
};

function draftKey(ids: string[]): string {
  return DRAFT_PREFIX + [...ids].sort().join(",");
}

/**
 * Batch deploy dialog. Given one or more selected templates, proposes an
 * area/department for each (metadata-driven, from the backend), lets the
 * operator edit the assignment, then dispatches one signed `deploy_agent`
 * command per agent — each carrying its area so the deployment manifest keeps
 * per-agent placement.
 */
export default function DeployPlanDialog({
  cards,
  onClose,
  onDeployed,
}: {
  cards: DeployCard[];
  onClose: () => void;
  onDeployed?: (instanceId: string, status: CommandStatus) => void;
}) {
  const toast = useOptionalToast();

  // Skills can't be deployed directly — filter them out of the plan.
  const deployable = useMemo(
    () => cards.filter((c) => c.artifact_type !== "skill"),
    [cards],
  );
  const skippedSkills = cards.length - deployable.length;
  const selectedIds = useMemo(() => deployable.map((c) => c.id), [deployable]);

  const [instances, setInstances] = useState<Instance[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [instanceId, setInstanceId] = useState<string | null>(null);

  const [rec, setRec] = useState<RecommendResponse | null>(null);
  const [recError, setRecError] = useState<string | null>(null);
  const [plan, setPlan] = useState<PlanEntry[]>([]);

  const [dispatching, setDispatching] = useState(false);
  const [statuses, setStatuses] = useState<Record<string, CommandStatus>>({});
  const [done, setDone] = useState(false);
  const pollAbort = useRef(false);

  // Restore any saved draft (manual choices + target instance) for this exact
  // selection so back-navigation / reloads don't lose work.
  const restoredRef = useRef(false);

  useEffect(() => {
    apiFetch<Instance[]>("/instances")
      .then((data) => {
        setInstances(data);
        const running = data.filter((i) => i.status === "running");
        if (running.length) setInstanceId((prev) => prev ?? running[0].instance_id);
      })
      .catch((e) => setLoadError(String(e)));
  }, []);

  useEffect(() => {
    if (selectedIds.length === 0) return;
    setRecError(null);
    apiFetch<RecommendResponse>("/agent-templates/recommend-areas", {
      method: "POST",
      body: JSON.stringify({ template_ids: selectedIds }),
    })
      .then(setRec)
      .catch((e) => setRecError(String(e)));
  }, [selectedIds]);

  // Reconcile recommendations into the editable plan whenever recs or the
  // selection change. Preserves manual overrides (see areaPlan.reconcilePlan).
  useEffect(() => {
    if (!rec) return;
    setPlan((prev) => {
      let next = reconcilePlan(prev, rec.recommendations, selectedIds);
      // One-time draft restore, applied after the first reconcile so the draft
      // wins over fresh auto-fill for manually-set agents.
      if (!restoredRef.current) {
        restoredRef.current = true;
        try {
          const raw = localStorage.getItem(draftKey(selectedIds));
          if (raw) {
            const saved = JSON.parse(raw) as {
              instanceId: string | null;
              manual: Record<string, string | null>;
            };
            if (saved.instanceId) setInstanceId(saved.instanceId);
            next = next.map((e) =>
              e.templateId in saved.manual
                ? { ...e, areaSlug: saved.manual[e.templateId], manual: true }
                : e,
            );
          }
        } catch {
          /* ignore malformed drafts */
        }
      }
      return next;
    });
  }, [rec, selectedIds]);

  // Persist the draft (manual choices only) as the operator edits.
  useEffect(() => {
    if (plan.length === 0) return;
    const manual: Record<string, string | null> = {};
    for (const e of plan) if (e.manual) manual[e.templateId] = e.areaSlug;
    try {
      localStorage.setItem(
        draftKey(selectedIds),
        JSON.stringify({ instanceId, manual }),
      );
    } catch {
      /* storage full / unavailable — non-fatal */
    }
  }, [plan, instanceId, selectedIds]);

  useEffect(() => () => {
    pollAbort.current = true;
  }, []);

  const areas: AreaOption[] = rec?.areas ?? [];
  const groups = useMemo(() => groupByArea(plan, areas), [plan, areas]);
  const unassigned = unassignedCount(plan);
  const runningInstances = instances?.filter((i) => i.status === "running") ?? [];

  const pollStatus = useCallback(
    async (iid: string, cmdId: string): Promise<CommandLog | null> => {
      for (let attempt = 0; attempt < 120; attempt++) {
        if (pollAbort.current) return null;
        try {
          const log = await apiFetch<CommandLog>(
            `/instances/${iid}/commands/${cmdId}`,
          );
          if (TERMINAL.includes(log.status)) return log;
        } catch {
          if (attempt > 5) return null;
        }
        await new Promise((r) => setTimeout(r, 500));
      }
      return null;
    },
    [],
  );

  const deploy = async () => {
    if (!instanceId || plan.length === 0) return;
    setDispatching(true);
    setDone(false);
    pollAbort.current = false;
    let applied = 0;
    let failed = 0;

    for (const entry of plan) {
      // On retry, don't re-deploy agents that already applied.
      if (statuses[entry.templateId] === "applied") {
        applied++;
        continue;
      }
      setStatuses((s) => ({ ...s, [entry.templateId]: "queued" }));
      try {
        const res = await apiFetch<CommandAccepted>(
          `/instances/${instanceId}/command`,
          {
            method: "POST",
            body: JSON.stringify({
              kind: "deploy_agent",
              payload: {
                template_id: entry.templateId,
                area: entry.areaSlug,
                area_source: entry.manual ? "manual" : entry.source,
              },
            }),
          },
        );
        setStatuses((s) => ({ ...s, [entry.templateId]: "in_progress" }));
        const final = await pollStatus(instanceId, res.cmd_id);
        const st = final?.status ?? "failed";
        setStatuses((s) => ({ ...s, [entry.templateId]: st }));
        if (st === "applied") applied++;
        else failed++;
      } catch (e) {
        setStatuses((s) => ({ ...s, [entry.templateId]: "failed" }));
        failed++;
      }
    }

    setDispatching(false);
    setDone(true);
    onDeployed?.(instanceId, failed === 0 ? "applied" : "failed");
    if (failed === 0) {
      toast.push({
        tone: "success",
        title: `Deployed ${applied} agent${applied === 1 ? "" : "s"}`,
        description: "All agents applied to their areas.",
        duration: 5000,
      });
      try {
        localStorage.removeItem(draftKey(selectedIds));
      } catch {
        /* ignore */
      }
    } else {
      toast.push({
        tone: "error",
        title: `${failed} of ${plan.length} agents failed`,
        description: "See per-agent status. You can retry.",
        duration: 8000,
      });
    }
  };

  const allApplied =
    done && plan.length > 0 && plan.every((e) => statuses[e.templateId] === "applied");

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Deploy agents with area assignment"
      data-testid="dialog-deploy-plan"
      onClick={onClose}
    >
      <div
        className="bg-surface border border-border rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2 min-w-0">
            <Sparkles className="w-4 h-4 text-primary" />
            <div className="min-w-0">
              <div className="text-sm font-semibold text-text">
                Deploy agents · proposed areas
              </div>
              <div className="text-xs text-text-muted">
                {deployable.length} agent{deployable.length === 1 ? "" : "s"} ·
                áreas propuestas automáticamente
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            data-testid="button-close-plan"
            className="text-text-muted hover:text-text p-1"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 overflow-auto flex-1 space-y-4">
          {skippedSkills > 0 && (
            <div className="flex items-start gap-2 p-3 rounded border border-warning/30 bg-warning/10 text-xs text-warning">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                {skippedSkills} skill{skippedSkills === 1 ? "" : "s"} skipped —
                skills are reusable capabilities and are not deployed directly.
              </div>
            </div>
          )}

          {/* Target instance */}
          <div>
            <div className="text-[11px] uppercase tracking-wide text-text-muted font-semibold mb-2">
              Target instance
            </div>
            {loadError && (
              <div className="text-xs text-error" data-testid="text-plan-instances-error">
                {loadError}
              </div>
            )}
            {!instances && !loadError && (
              <div className="text-xs text-text-muted">Loading instances…</div>
            )}
            {instances && runningInstances.length === 0 && (
              <div
                className="text-xs text-text-muted p-3 border border-dashed border-border rounded"
                data-testid="text-plan-no-instances"
              >
                No running instances. Start or bootstrap one from the Instances
                page first.
              </div>
            )}
            <div className="space-y-1.5">
              {runningInstances.map((inst) => {
                const active = instanceId === inst.instance_id;
                return (
                  <button
                    key={inst.instance_id}
                    onClick={() => setInstanceId(inst.instance_id)}
                    data-testid={`option-plan-instance-${inst.instance_id}`}
                    className={`w-full text-left border rounded p-2.5 transition-colors ${
                      active
                        ? "border-primary bg-surface-alt"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm text-text truncate">
                        {inst.name}
                      </span>
                      <span className="text-[11px] text-success">{inst.status}</span>
                    </div>
                    <div className="text-[11px] text-text-muted mt-0.5 truncate">
                      {inst.persona_display_name} · {inst.modality}
                      {inst.version && <> · v{inst.version}</>}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Proposals */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="text-[11px] uppercase tracking-wide text-text-muted font-semibold">
                Proposed areas
              </div>
              <button
                onClick={() => setPlan((p) => acceptAllRecommendations(p))}
                disabled={plan.length === 0 || dispatching}
                data-testid="button-accept-all"
                className="text-[11px] font-medium text-primary hover:underline disabled:opacity-40 disabled:no-underline"
              >
                Accept all suggestions
              </button>
            </div>

            {recError && (
              <div className="text-xs text-error" data-testid="text-plan-rec-error">
                Failed to load recommendations: {recError}
              </div>
            )}
            {!rec && !recError && (
              <div className="text-xs text-text-muted">Proposing areas…</div>
            )}

            {rec && (
              <div className="space-y-3" data-testid="plan-groups">
                {groups.map((g) => (
                  <div
                    key={g.slug ?? "__unassigned"}
                    data-testid={`area-group-${g.slug ?? "unassigned"}`}
                    className="border border-border rounded-lg overflow-hidden"
                  >
                    <div className="flex items-center justify-between px-3 py-2 bg-surface-alt border-b border-border">
                      <span className="text-sm font-medium text-text">
                        {g.label}
                      </span>
                      <span className="text-[11px] text-text-muted">
                        {g.entries.length} agent{g.entries.length === 1 ? "" : "s"}
                      </span>
                    </div>
                    <div className="divide-y divide-border">
                      {g.entries.map((e) => (
                        <PlanRow
                          key={e.templateId}
                          entry={e}
                          areas={areas}
                          status={statuses[e.templateId]}
                          disabled={dispatching}
                          onChange={(slug) =>
                            setPlan((p) => setAreaManually(p, e.templateId, slug))
                          }
                          onReset={() =>
                            setPlan((p) => resetToRecommendation(p, e.templateId))
                          }
                          onRemove={
                            plan.length > 1 && !done
                              ? () =>
                                  setPlan((p) =>
                                    p.filter((x) => x.templateId !== e.templateId),
                                  )
                              : undefined
                          }
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {rec && unassigned > 0 && (
              <div
                className="mt-2 text-[11px] text-text-muted"
                data-testid="text-unassigned-note"
              >
                {unassigned} agent{unassigned === 1 ? "" : "s"} unassigned —
                allowed, but they will deploy without an area.
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 p-3 border-t border-border">
          <div className="text-[11px] text-text-muted">
            {done
              ? allApplied
                ? "All agents applied."
                : "Some agents failed — retry or close."
              : "Recommendations are editable before deploy."}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              data-testid="button-cancel-plan"
              className="px-3 py-1.5 text-sm text-text-muted hover:text-text"
            >
              {done ? "Close" : "Cancel"}
            </button>
            <button
              onClick={deploy}
              disabled={
                !instanceId || plan.length === 0 || dispatching || allApplied
              }
              data-testid="button-deploy-plan"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded bg-primary text-white hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {done && !allApplied ? (
                <RotateCcw className="w-3.5 h-3.5" />
              ) : (
                <Rocket className="w-3.5 h-3.5" />
              )}
              {dispatching
                ? "Deploying…"
                : done && !allApplied
                  ? "Retry failed"
                  : `Deploy ${plan.length}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function PlanRow({
  entry,
  areas,
  status,
  disabled,
  onChange,
  onReset,
  onRemove,
}: {
  entry: PlanEntry;
  areas: AreaOption[];
  status?: CommandStatus;
  disabled: boolean;
  onChange: (slug: string | null) => void;
  onReset: () => void;
  onRemove?: () => void;
}) {
  return (
    <div
      className="flex items-center gap-3 px-3 py-2"
      data-testid={`plan-row-${entry.templateId}`}
    >
      <div className="min-w-0 flex-1">
        <div className="font-mono text-sm text-text truncate">
          {entry.templateId}
        </div>
        <div
          className="text-[11px] text-text-muted truncate"
          data-testid={`plan-rationale-${entry.templateId}`}
        >
          <span className="inline-flex items-center gap-1">
            <span className="px-1.5 py-0.5 rounded bg-surface-alt border border-border text-[10px]">
              {SOURCE_LABEL[entry.source]}
            </span>
            {entry.rationale}
          </span>
        </div>
      </div>

      {status && (
        <span
          data-testid={`plan-status-${entry.templateId}`}
          data-status={status}
          className={`text-[11px] font-medium ${
            status === "applied"
              ? "text-success"
              : status === "failed" || status === "rejected"
                ? "text-error"
                : "text-primary animate-pulse"
          }`}
        >
          {status === "applied" ? (
            <Check className="w-3.5 h-3.5 inline" />
          ) : (
            status
          )}
        </span>
      )}

      <select
        value={entry.areaSlug ?? ""}
        disabled={disabled}
        onChange={(ev) => onChange(ev.target.value === "" ? null : ev.target.value)}
        data-testid={`plan-area-select-${entry.templateId}`}
        aria-label={`Area for ${entry.templateId}`}
        className="text-xs bg-bg border border-border rounded px-2 py-1 focus:outline-none focus:border-primary disabled:opacity-50"
      >
        <option value="">Unassigned</option>
        {areas.map((a) => (
          <option key={a.slug} value={a.slug}>
            {a.label}
          </option>
        ))}
      </select>

      {entry.manual && entry.recommendedSlug !== entry.areaSlug && (
        <button
          onClick={onReset}
          disabled={disabled}
          data-testid={`plan-reset-${entry.templateId}`}
          title="Reset to suggestion"
          className="text-text-muted hover:text-text p-1 disabled:opacity-40"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      )}
      {onRemove && (
        <button
          onClick={onRemove}
          data-testid={`plan-remove-${entry.templateId}`}
          title="Remove from this deployment"
          className="text-text-muted hover:text-error p-1"
          aria-label={`Remove ${entry.templateId}`}
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
