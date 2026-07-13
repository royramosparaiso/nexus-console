import type { LlmConfig, LlmProvider, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Props = {
  schema: WizardSchema;
  value: LlmConfig;
  onChange: (patch: Partial<LlmConfig>) => void;
};

export default function Step3Llms({ schema, value, onChange }: Props) {
  const toggleProvider = (p: LlmProvider) => {
    const set = new Set(value.enabled_providers);
    if (set.has(p)) set.delete(p);
    else set.add(p);
    onChange({ enabled_providers: Array.from(set) as LlmProvider[] });
  };

  return (
    <StepShell
      index={3}
      total={6}
      title="LLM providers"
      description="Which providers this instance can call, and which model powers each router role."
    >
      <Field label="Enabled providers" hint="At least one required. Configure API keys later in LLM Providers." testid="field-providers">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {schema.llm_providers.map((p) => {
            const active = value.enabled_providers.includes(p);
            return (
              <button
                type="button"
                key={p}
                onClick={() => toggleProvider(p)}
                className={`border rounded-md px-3 py-2 text-sm capitalize transition-colors ${
                  active
                    ? "border-primary bg-surface-alt text-text"
                    : "border-border text-text-muted hover:border-text-faint hover:text-text"
                }`}
                data-testid={`toggle-provider-${p}`}
              >
                {p}
              </button>
            );
          })}
        </div>
      </Field>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Planner model" hint="High-reasoning orchestrator." testid="field-role-planner">
          <input
            className={inputCls}
            value={value.roles.planner}
            onChange={(e) => onChange({ roles: { ...value.roles, planner: e.target.value } })}
            data-testid="input-role-planner"
          />
        </Field>
        <Field label="Coordinator model" hint="Mid-tier area coordinators." testid="field-role-coordinator">
          <input
            className={inputCls}
            value={value.roles.coordinator}
            onChange={(e) => onChange({ roles: { ...value.roles, coordinator: e.target.value } })}
            data-testid="input-role-coordinator"
          />
        </Field>
        <Field label="Worker model" hint="Cheap/fast high-volume workers." testid="field-role-worker">
          <input
            className={inputCls}
            value={value.roles.worker}
            onChange={(e) => onChange({ roles: { ...value.roles, worker: e.target.value } })}
            data-testid="input-role-worker"
          />
        </Field>
        <Field label="Embeddings model" testid="field-role-embeddings">
          <input
            className={inputCls}
            value={value.roles.embeddings}
            onChange={(e) => onChange({ roles: { ...value.roles, embeddings: e.target.value } })}
            data-testid="input-role-embeddings"
          />
        </Field>
      </div>

      <div className="flex items-center gap-6 pt-2">
        <label className="flex items-center gap-2 text-sm text-text" data-testid="field-fallback">
          <input
            type="checkbox"
            checked={value.allow_fallback}
            onChange={(e) => onChange({ allow_fallback: e.target.checked })}
            data-testid="check-fallback"
          />
          Allow provider fallback
        </label>
        <Field label="Monthly budget (USD)" testid="field-budget">
          <input
            type="number"
            min={0}
            step="1"
            className={`${inputCls} w-32`}
            value={value.monthly_budget_usd}
            onChange={(e) => onChange({ monthly_budget_usd: Number(e.target.value) })}
            data-testid="input-budget"
          />
        </Field>
      </div>
    </StepShell>
  );
}
