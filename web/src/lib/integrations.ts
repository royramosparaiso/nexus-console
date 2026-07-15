/**
 * integrations.ts — types + pure helpers for the integration adapter layer
 * served by the Console backend under /integrations. Framework-free so the
 * form-building, validation, and probe-state mapping logic are unit-testable
 * without React.
 *
 * Security note: secrets are only ever referenced by environment-variable
 * NAME. This module never carries a secret value; the create payload sends
 * env-name references and the backend reads the value at probe time.
 */

export interface SecretSpec {
  key: string;
  label: string;
  env: string;
  required: boolean;
}

export interface FieldSpec {
  key: string;
  label: string;
  default: string | null;
  required: boolean;
  placeholder: string | null;
}

export interface Adapter {
  id: string;
  name: string;
  category: string;
  provider: string;
  capabilities: string[];
  probe: string;
  integration: "native" | "external";
  base_url_default: string | null;
  fields: FieldSpec[];
  secrets: SecretSpec[];
  docs_url: string | null;
  template_id: string | null;
  tags: string[];
  notes: string | null;
}

/** Per-secret redacted view returned by the profiles API — never a value. */
export interface SecretRefView {
  key: string;
  label: string;
  env: string | null;
  required: boolean;
  present: boolean;
}

export interface Profile {
  id: string;
  adapter_id: string;
  name: string;
  base_url: string | null;
  config: Record<string, unknown>;
  secret_refs: SecretRefView[];
  template_ids: string[];
  enabled: boolean;
  capabilities: string[];
  created_at: string;
  updated_at: string;
}

export interface ProfileCreate {
  adapter_id: string;
  name: string;
  base_url: string | null;
  config: Record<string, string>;
  secret_refs: Record<string, string>;
  template_ids: string[];
  enabled: boolean;
}

export type ProbeState =
  | "reachable"
  | "unreachable"
  | "unconfigured"
  | "invalid_url"
  | "secret_missing"
  | "no_probe";

export interface ProbeResult {
  state: string;
  detail: string | null;
  latency_ms: number | null;
  checked_url: string | null;
}

export interface ProbeStateMeta {
  label: string;
  /** Tailwind classes using the existing design tokens. */
  className: string;
}

const PROBE_STATE_META: Record<ProbeState, ProbeStateMeta> = {
  reachable: { label: "Reachable", className: "text-success" },
  unreachable: { label: "Unreachable", className: "text-error" },
  unconfigured: { label: "Not configured", className: "text-text-muted" },
  invalid_url: { label: "Invalid URL", className: "text-error" },
  secret_missing: { label: "Secret missing", className: "text-warning" },
  no_probe: { label: "No probe", className: "text-text-muted" },
};

export function probeStateMeta(state: string): ProbeStateMeta {
  return (
    PROBE_STATE_META[state as ProbeState] ?? {
      label: state,
      className: "text-text-muted",
    }
  );
}

/**
 * An env-var reference must look like an env name, never a value: no spaces,
 * reasonably short. Mirrors the backend guard so the UI can flag mistakes
 * before a round-trip.
 */
export function isValidEnvRef(name: string): boolean {
  return name.length > 0 && name.length <= 128 && !/\s/.test(name);
}

/**
 * A base_url is optional; when present it must be an http(s) URL with a host.
 * Empty string is treated as "unset" (backend normalises to null).
 */
export function isValidBaseUrl(url: string): boolean {
  if (url === "") return true;
  try {
    const u = new URL(url);
    return (u.protocol === "http:" || u.protocol === "https:") && u.host !== "";
  } catch {
    return false;
  }
}

/**
 * Build a create payload from raw form inputs, dropping blank optional secret
 * refs and blank config fields so we never send empty env names.
 */
export function buildCreatePayload(
  adapter: Adapter,
  form: {
    name: string;
    base_url: string;
    config: Record<string, string>;
    secret_refs: Record<string, string>;
    template_ids: string[];
    enabled: boolean;
  },
): ProfileCreate {
  const secret_refs: Record<string, string> = {};
  for (const [k, v] of Object.entries(form.secret_refs)) {
    if (v && v.trim() !== "") secret_refs[k] = v.trim();
  }
  const config: Record<string, string> = {};
  for (const [k, v] of Object.entries(form.config)) {
    if (v && v.trim() !== "") config[k] = v.trim();
  }
  return {
    adapter_id: adapter.id,
    name: form.name.trim(),
    base_url: form.base_url.trim() === "" ? null : form.base_url.trim(),
    config,
    secret_refs,
    template_ids: form.template_ids,
    enabled: form.enabled,
  };
}

/**
 * Default env-name references for an adapter's secrets, so the form starts
 * pre-filled with the adapter's declared env names (operators usually keep
 * them).
 */
export function defaultSecretRefs(adapter: Adapter): Record<string, string> {
  const refs: Record<string, string> = {};
  for (const s of adapter.secrets) refs[s.key] = s.env;
  return refs;
}

/** Client-side validation errors for a create form. Empty ⇒ ok to submit. */
export function validateProfileForm(
  adapter: Adapter,
  form: { name: string; base_url: string; secret_refs: Record<string, string> },
): string[] {
  const errors: string[] = [];
  if (form.name.trim() === "") errors.push("Name is required.");
  if (!isValidBaseUrl(form.base_url))
    errors.push("Base URL must be an http(s) URL with a host.");
  for (const s of adapter.secrets) {
    const ref = (form.secret_refs[s.key] ?? "").trim();
    if (s.required && ref === "")
      errors.push(`${s.label} needs an environment-variable name.`);
    if (ref !== "" && !isValidEnvRef(ref))
      errors.push(`${s.label} must be an environment-variable name, not a value.`);
  }
  return errors;
}
