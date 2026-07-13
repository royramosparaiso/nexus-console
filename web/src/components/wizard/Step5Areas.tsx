import type { AreasConfig, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field } from "./StepShell";

type Props = {
  schema: WizardSchema;
  value: AreasConfig;
  onChange: (patch: Partial<AreasConfig>) => void;
};

export default function Step5Areas({ schema, value, onChange }: Props) {
  const toggle = (slug: string) => {
    const set = new Set(value.enabled);
    if (set.has(slug)) set.delete(slug);
    else set.add(slug);
    onChange({ enabled: Array.from(set) });
  };

  const core = schema.available_areas.filter((a) => a.tier === "core");
  const vertical = schema.available_areas.filter((a) => a.tier === "vertical");

  return (
    <StepShell
      index={5}
      total={6}
      title="Active areas"
      description="Which agent areas are deployed to this instance at bootstrap. You can enable more later."
    >
      <Field label="Core areas" hint="Recommended for every instance." testid="field-areas-core">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {core.map((a) => (
            <AreaCheckbox key={a.slug} slug={a.slug} label={a.label} checked={value.enabled.includes(a.slug)} onToggle={toggle} />
          ))}
        </div>
      </Field>

      <Field label="Vertical areas" hint="Optional — enable only what this instance actually needs." testid="field-areas-vertical">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {vertical.map((a) => (
            <AreaCheckbox key={a.slug} slug={a.slug} label={a.label} checked={value.enabled.includes(a.slug)} onToggle={toggle} />
          ))}
        </div>
      </Field>
    </StepShell>
  );
}

function AreaCheckbox({
  slug,
  label,
  checked,
  onToggle,
}: {
  slug: string;
  label: string;
  checked: boolean;
  onToggle: (slug: string) => void;
}) {
  return (
    <label
      className={`border rounded-md px-3 py-2 flex items-center gap-3 cursor-pointer transition-colors ${
        checked ? "border-primary bg-surface-alt" : "border-border hover:border-text-faint"
      }`}
      data-testid={`toggle-area-${slug}`}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={() => onToggle(slug)}
        data-testid={`check-area-${slug}`}
      />
      <span className="text-sm text-text">{label}</span>
    </label>
  );
}
