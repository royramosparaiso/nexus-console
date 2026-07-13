import type { AutonomyLevel, GovernanceConfig, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Props = {
  schema: WizardSchema;
  value: GovernanceConfig;
  onChange: (patch: Partial<GovernanceConfig>) => void;
};

export default function Step6Governance({ schema, value, onChange }: Props) {
  return (
    <StepShell
      index={6}
      total={6}
      title="Governance"
      description="Global ceilings and safety controls. Individual spaces can only tighten these."
    >
      <Field label="Default autonomy level" testid="field-autonomy">
        <select
          className={inputCls}
          value={value.default_autonomy}
          onChange={(e) => onChange({ default_autonomy: e.target.value as AutonomyLevel })}
          data-testid="select-autonomy"
        >
          {schema.autonomy_levels.map((a) => (
            <option key={a.value} value={a.value}>{a.label}</option>
          ))}
        </select>
      </Field>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Audit retention (days)" hint="90 to 3650." testid="field-audit-retention">
          <input
            type="number"
            min={90}
            max={3650}
            className={inputCls}
            value={value.audit_retention_days}
            onChange={(e) => onChange({ audit_retention_days: Number(e.target.value) })}
            data-testid="input-audit-retention"
          />
        </Field>
        <Field label="Budget alert (% of monthly)" hint="Fires notification at this threshold." testid="field-budget-alert">
          <input
            type="number"
            min={10}
            max={100}
            className={inputCls}
            value={value.monthly_budget_alert_pct}
            onChange={(e) => onChange({ monthly_budget_alert_pct: Number(e.target.value) })}
            data-testid="input-budget-alert"
          />
        </Field>
      </div>

      <div className="space-y-2 pt-2">
        <label className="flex items-center gap-2 text-sm text-text" data-testid="field-kill-switch">
          <input
            type="checkbox"
            checked={value.kill_switch_enabled}
            onChange={(e) => onChange({ kill_switch_enabled: e.target.checked })}
            data-testid="check-kill-switch"
          />
          Enable global kill-switch
        </label>
        <label className="flex items-center gap-2 text-sm text-text" data-testid="field-2fa">
          <input
            type="checkbox"
            checked={value.require_2fa_for_superadmin}
            onChange={(e) => onChange({ require_2fa_for_superadmin: e.target.checked })}
            data-testid="check-2fa"
          />
          Require 2FA for <code className="text-xs bg-surface-alt px-1 py-0.5 rounded">superadmin</code>
        </label>
      </div>
    </StepShell>
  );
}
