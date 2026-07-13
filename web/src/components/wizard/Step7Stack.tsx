/**
 * Step 7 — Stack.
 *
 * Operator picks a monthly cloud budget and deployment mode; the console
 * asks the backend recommender for a concrete service pick per role, then
 * shows the result. Any role can be overridden manually before submit.
 */

import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import type {
  BudgetTier,
  DeploymentMode,
  StackConfig,
  StackPreferences,
  StackRole,
  StackSelection,
  StackService,
} from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Catalog = {
  services: StackService[];
  by_role: Record<StackRole, StackService[]>;
  standard_100_eur_stack: Record<StackRole, string>;
};

type Props = {
  value: StackConfig | null | undefined;
  onChange: (next: StackConfig) => void;
};

const ROLE_LABELS: Record<StackRole, string> = {
  app_compute: "App compute",
  frontend_hosting: "Frontend hosting",
  postgres: "Postgres",
  graph_db: "Graph DB",
  vector_db: "Vector DB",
  cache_queue: "Cache / queue",
  gpu_serverless: "GPU serverless",
  llm_gateway: "LLM gateway",
  object_storage: "Object storage",
  auth: "Authentication",
  dns_cdn: "DNS + CDN",
  error_monitoring: "Error monitoring",
  log_platform: "Logs",
  product_analytics: "Product analytics",
  llm_observability: "LLM observability",
  email_transactional: "Transactional email",
  background_jobs: "Background jobs",
  ci_cd: "CI / CD",
};

const DEFAULT_PREFS: StackPreferences = {
  monthly_budget_eur: 100,
  deployment_mode: "cloud",
  team_size: 4,
  needs_graph_db: true,
  needs_voice_gpu: true,
  needs_llm_observability: true,
  needs_product_analytics: true,
  needs_background_jobs: true,
  prefer_open_source: false,
  prefer_scale_to_zero: true,
  region: "eu",
};

const TIER_COLORS: Record<BudgetTier, string> = {
  free: "text-slate-500 bg-slate-500/10",
  hobby: "text-emerald-600 bg-emerald-500/10",
  standard: "text-indigo-600 bg-indigo-500/10",
  scale: "text-orange-600 bg-orange-500/10",
};

export default function Step7Stack({ value, onChange }: Props) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [prefs, setPrefs] = useState<StackPreferences>(
    value?.preferences ?? DEFAULT_PREFS,
  );
  const [selection, setSelection] = useState<StackSelection | null>(
    value?.selection ?? null,
  );
  const [overrides, setOverrides] = useState<Partial<Record<StackRole, string>>>(
    value?.overrides ?? {},
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load catalogue once.
  useEffect(() => {
    let cancelled = false;
    apiFetch<Catalog>("/wizard/stack/catalog")
      .then((cat) => { if (!cancelled) setCatalog(cat); })
      .catch((e) => { if (!cancelled) setError(String(e)); });
    return () => { cancelled = true; };
  }, []);

  // Fetch a recommendation whenever prefs change.
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    apiFetch<StackSelection>("/wizard/stack/recommend", {
      method: "POST",
      body: JSON.stringify(prefs),
    })
      .then((sel) => {
        if (cancelled) return;
        setSelection(sel);
        // Reset overrides when tier or mode change materially.
        setOverrides((prev) => {
          const kept: Partial<Record<StackRole, string>> = {};
          for (const [role, slug] of Object.entries(prev) as [StackRole, string][]) {
            // Only keep overrides whose role is still present in the selection.
            if (role in sel.services) kept[role] = slug;
          }
          return kept;
        });
      })
      .catch((e) => { if (!cancelled) setError(String(e)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [prefs]);

  // Push the assembled StackConfig upstream every time anything changes.
  useEffect(() => {
    if (!selection) return;
    onChange({ preferences: prefs, selection, overrides });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prefs, selection, overrides]);

  const effective: Partial<Record<StackRole, string>> = useMemo(() => {
    if (!selection) return {};
    return { ...selection.services, ...overrides };
  }, [selection, overrides]);

  return (
    <StepShell
      index={7}
      total={7}
      title="Stack"
      description="Managed services this instance will use. Answer the questions and we recommend a stack; override any role."
    >
      {/* -------- Preferences -------- */}
      <Field label="Monthly cloud budget (EUR)" hint="Excludes local compute. ~€100 activates the standard cloud stack." testid="field-budget">
        <input
          type="number"
          className={inputCls}
          min={0}
          max={10000}
          step={5}
          value={prefs.monthly_budget_eur}
          onChange={(e) => setPrefs((p) => ({ ...p, monthly_budget_eur: Number(e.target.value) }))}
          data-testid="input-monthly-budget"
        />
      </Field>

      <Field label="Deployment mode" testid="field-deployment-mode">
        <select
          className={inputCls}
          value={prefs.deployment_mode}
          onChange={(e) => setPrefs((p) => ({ ...p, deployment_mode: e.target.value as DeploymentMode }))}
          data-testid="select-deployment-mode"
        >
          <option value="cloud">Cloud (managed services)</option>
          <option value="hybrid">Hybrid (some local, some cloud)</option>
          <option value="local">Local only (self-hosted)</option>
        </select>
      </Field>

      <Field label="Team size" testid="field-team-size">
        <input
          type="number"
          className={inputCls}
          min={1}
          max={10000}
          value={prefs.team_size}
          onChange={(e) => setPrefs((p) => ({ ...p, team_size: Number(e.target.value) }))}
          data-testid="input-team-size"
        />
      </Field>

      <div className="grid grid-cols-2 gap-2 pt-2" data-testid="group-needs">
        {[
          ["needs_graph_db", "Graph DB (Neo4j-style)"],
          ["needs_voice_gpu", "Voice / GPU inference"],
          ["needs_llm_observability", "LLM observability (Langfuse)"],
          ["needs_product_analytics", "Product analytics + logs"],
          ["needs_background_jobs", "Background jobs + email"],
          ["prefer_open_source", "Prefer open-source vendors"],
          ["prefer_scale_to_zero", "Prefer scale-to-zero pricing"],
        ].map(([key, label]) => (
          <label key={key} className="flex items-center gap-2 text-sm text-text-primary">
            <input
              type="checkbox"
              checked={Boolean((prefs as any)[key])}
              onChange={(e) => setPrefs((p) => ({ ...p, [key]: e.target.checked } as StackPreferences))}
              data-testid={`checkbox-${key}`}
            />
            {label}
          </label>
        ))}
      </div>

      {/* -------- Recommendation -------- */}
      <div className="mt-6 rounded-lg border border-border bg-surface-alt p-4" data-testid="stack-preview">
        {error && (
          <div className="text-sm text-red-500" data-testid="text-stack-error">{error}</div>
        )}
        {loading && !selection && (
          <div className="text-sm text-text-muted">Computing recommendation…</div>
        )}
        {selection && (
          <>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${TIER_COLORS[selection.tier]}`} data-testid="badge-tier">
                  {selection.tier.toUpperCase()}
                </span>
                <span className="text-sm text-text-muted">
                  ≈ ${selection.estimated_monthly_usd.toFixed(0)} / month
                </span>
              </div>
              {loading && <span className="text-xs text-text-muted">refreshing…</span>}
            </div>
            <p className="text-sm text-text-muted mb-4" data-testid="text-rationale">
              {selection.rationale}
            </p>

            <div className="space-y-1.5">
              {Object.entries(effective).map(([role, slug]) => {
                const r = role as StackRole;
                const svc = catalog?.services.find((s) => s.slug === slug);
                const options = catalog?.by_role[r] ?? [];
                return (
                  <div
                    key={role}
                    className="flex items-center justify-between gap-3 text-sm"
                    data-testid={`row-service-${role}`}
                  >
                    <span className="text-text-muted min-w-[10rem]">{ROLE_LABELS[r]}</span>
                    <select
                      className={`${inputCls} !py-1 !text-xs flex-1`}
                      value={slug}
                      onChange={(e) => {
                        const newSlug = e.target.value;
                        setOverrides((prev) => {
                          const copy = { ...prev };
                          if (newSlug === selection.services[r]) {
                            delete copy[r];
                          } else {
                            copy[r] = newSlug;
                          }
                          return copy;
                        });
                      }}
                      data-testid={`select-service-${role}`}
                    >
                      {options.map((opt) => (
                        <option key={opt.slug} value={opt.slug}>
                          {opt.name} — ${opt.price_entry_usd || opt.price_free_usd}/mo
                        </option>
                      ))}
                    </select>
                    {svc?.homepage && (
                      <a
                        href={svc.homepage}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:underline"
                        data-testid={`link-service-${role}`}
                      >
                        docs
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </StepShell>
  );
}
