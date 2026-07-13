import type { PersonaConfig, PersonaKind, WizardSchema } from "@/lib/wizardTypes";
import StepShell, { Field, inputCls } from "./StepShell";

type Props = {
  schema: WizardSchema;
  instanceName: string;
  onInstanceNameChange: (v: string) => void;
  value: PersonaConfig;
  onChange: (patch: Partial<PersonaConfig>) => void;
};

export default function Step1Persona({
  schema,
  instanceName,
  onInstanceNameChange,
  value,
  onChange,
}: Props) {
  return (
    <StepShell
      index={1}
      total={6}
      title="Persona"
      description="How this instance identifies itself inside the Nexus framework."
    >
      <Field label="Instance name (slug)" hint="Lowercase, no spaces. Used internally." testid="field-instance-name">
        <input
          className={inputCls}
          value={instanceName}
          onChange={(e) => onInstanceNameChange(e.target.value.toLowerCase().replace(/\s+/g, "-"))}
          placeholder="ironbat"
          data-testid="input-instance-name"
        />
      </Field>

      <Field label="Display name" hint="Public-facing name of this persona." testid="field-display-name">
        <input
          className={inputCls}
          value={value.display_name}
          onChange={(e) => onChange({ display_name: e.target.value })}
          placeholder="Ironbat"
          data-testid="input-display-name"
        />
      </Field>

      <Field label="Persona kind" testid="field-persona-kind">
        <select
          className={inputCls}
          value={value.kind}
          onChange={(e) => onChange({ kind: e.target.value as PersonaKind })}
          data-testid="select-persona-kind"
        >
          {schema.persona_kinds.map((k) => (
            <option key={k.value} value={k.value}>{k.label}</option>
          ))}
        </select>
      </Field>

      <Field label="Description" hint="Optional — short description for the operator." testid="field-description">
        <textarea
          className={inputCls}
          rows={2}
          value={value.description}
          onChange={(e) => onChange({ description: e.target.value })}
          data-testid="input-description"
        />
      </Field>

      <Field label="Default locale" hint="Format: xx-YY (e.g. es-ES, en-US)." testid="field-locale">
        <input
          className={inputCls}
          value={value.default_locale}
          onChange={(e) => onChange({ default_locale: e.target.value })}
          placeholder="es-ES"
          data-testid="input-locale"
        />
      </Field>
    </StepShell>
  );
}
