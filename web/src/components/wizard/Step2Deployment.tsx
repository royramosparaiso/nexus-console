import type { DeploymentConfig, Modality, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Props = {
  schema: WizardSchema;
  value: DeploymentConfig;
  onChange: (patch: Partial<DeploymentConfig>) => void;
};

export default function Step2Deployment({ schema, value, onChange }: Props) {
  const isLocal = value.modality === "local";
  return (
    <StepShell
      index={2}
      total={6}
      title="Deployment"
      description="Where the Platform instance will run."
    >
      <Field label="Modality" testid="field-modality">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {schema.modalities.map((m) => (
            <button
              type="button"
              key={m.value}
              onClick={() => onChange({ modality: m.value as Modality })}
              className={`text-left border rounded-md px-3 py-2 text-sm transition-colors ${
                value.modality === m.value
                  ? "border-primary bg-surface-alt text-text"
                  : "border-border text-text-muted hover:border-text-faint hover:text-text"
              }`}
              data-testid={`option-modality-${m.value}`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </Field>

      <Field label="Domain" hint={isLocal ? "Ignored in local mode." : "e.g. nexus.example.com"} testid="field-domain">
        <input
          className={inputCls}
          value={value.domain ?? ""}
          onChange={(e) => onChange({ domain: e.target.value || null })}
          disabled={isLocal}
          placeholder="nexus.example.com"
          data-testid="input-domain"
        />
      </Field>

      {!isLocal && (
        <Field label="Region" hint="Cloud region (fly: ams, mad, etc.)" testid="field-region">
          <input
            className={inputCls}
            value={value.region ?? ""}
            onChange={(e) => onChange({ region: e.target.value || null })}
            placeholder="ams"
            data-testid="input-region"
          />
        </Field>
      )}

      <div className="flex items-center gap-6 pt-2">
        <label className="flex items-center gap-2 text-sm text-text" data-testid="field-tls">
          <input
            type="checkbox"
            checked={value.tls}
            onChange={(e) => onChange({ tls: e.target.checked })}
            data-testid="check-tls"
          />
          Enable TLS
        </label>
        {!isLocal && (
          <label className="flex items-center gap-2 text-sm text-text" data-testid="field-autoscale">
            <input
              type="checkbox"
              checked={value.autoscale}
              onChange={(e) => onChange({ autoscale: e.target.checked })}
              data-testid="check-autoscale"
            />
            Autoscale
          </label>
        )}
      </div>
    </StepShell>
  );
}
