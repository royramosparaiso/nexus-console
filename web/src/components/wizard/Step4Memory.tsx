import type { GraphDriver, MemoryConfig, MemoryDriver, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Props = {
  schema: WizardSchema;
  value: MemoryConfig;
  onChange: (patch: Partial<MemoryConfig>) => void;
};

export default function Step4Memory({ schema, value, onChange }: Props) {
  return (
    <StepShell
      index={4}
      total={6}
      title="Memory & graph"
      description="Storage layer for scoped memory and knowledge graph."
    >
      <Field label="Memory driver" testid="field-memory-driver">
        <select
          className={inputCls}
          value={value.driver}
          onChange={(e) => onChange({ driver: e.target.value as MemoryDriver })}
          data-testid="select-memory-driver"
        >
          {schema.memory_drivers.map((d) => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
      </Field>

      <Field label="Knowledge graph" testid="field-graph">
        <select
          className={inputCls}
          value={value.graph}
          onChange={(e) => onChange({ graph: e.target.value as GraphDriver })}
          data-testid="select-graph"
        >
          {schema.graph_drivers.map((d) => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
      </Field>

      <Field label="Retention (days)" hint="7 to 3650. Older entries are archived or purged." testid="field-retention">
        <input
          type="number"
          min={7}
          max={3650}
          className={`${inputCls} w-40`}
          value={value.retention_days}
          onChange={(e) => onChange({ retention_days: Number(e.target.value) })}
          data-testid="input-retention"
        />
      </Field>

      <label className="flex items-center gap-2 text-sm text-text" data-testid="field-encryption">
        <input
          type="checkbox"
          checked={value.encryption_at_rest}
          onChange={(e) => onChange({ encryption_at_rest: e.target.checked })}
          data-testid="check-encryption"
        />
        Encryption at rest
      </label>
    </StepShell>
  );
}
