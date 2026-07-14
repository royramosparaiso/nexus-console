/**
 * IntegrationsManager — configure the generic integration adapters from the
 * Ecosystem page. Lists the adapter catalogue, lets an operator create a
 * connection profile (endpoint + secret env-name references, never values),
 * run a health probe ("Test connection"), enable/disable, and delete.
 *
 * Secret handling: the form only ever collects environment-variable NAMES.
 * The real value lives in the process environment and is read by the backend
 * at probe time — it is never sent from or shown in the browser.
 */

import { useEffect, useMemo, useState } from "react";
import { Plug, RefreshCw, Trash2 } from "lucide-react";

import { apiFetch } from "../lib/api";
import { useToast } from "./Toast";
import {
  buildCreatePayload,
  defaultSecretRefs,
  probeStateMeta,
  validateProfileForm,
  type Adapter,
  type Profile,
  type ProbeResult,
} from "../lib/integrations";

interface FormState {
  name: string;
  base_url: string;
  secret_refs: Record<string, string>;
  enabled: boolean;
}

function emptyForm(adapter: Adapter): FormState {
  return {
    name: "",
    base_url: adapter.base_url_default ?? "",
    secret_refs: defaultSecretRefs(adapter),
    enabled: false,
  };
}

function CreateForm({
  adapter,
  onCreated,
}: {
  adapter: Adapter;
  onCreated: () => void;
}) {
  const { push } = useToast();
  const [form, setForm] = useState<FormState>(() => emptyForm(adapter));
  const [saving, setSaving] = useState(false);

  useEffect(() => setForm(emptyForm(adapter)), [adapter]);

  const errors = useMemo(
    () => validateProfileForm(adapter, form),
    [adapter, form],
  );

  const submit = async () => {
    if (errors.length > 0) return;
    setSaving(true);
    try {
      await apiFetch("/integrations/profiles", {
        method: "POST",
        body: JSON.stringify(
          buildCreatePayload(adapter, { ...form, config: {}, template_ids: [] }),
        ),
      });
      push({ tone: "success", title: `Saved ${adapter.name} profile` });
      onCreated();
    } catch (e) {
      push({ tone: "error", title: "Could not save profile", description: String(e) });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3" data-testid={`form-create-${adapter.id}`}>
      <label className="block">
        <span className="text-xs text-text-faint">Profile name</span>
        <input
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          placeholder="prod"
          data-testid="input-profile-name"
          className="mt-1 w-full rounded-md border border-border bg-bg px-2 py-1.5 text-sm text-text"
        />
      </label>

      <label className="block">
        <span className="text-xs text-text-faint">Base URL {adapter.base_url_default ? "" : "(optional)"}</span>
        <input
          value={form.base_url}
          onChange={(e) => setForm({ ...form, base_url: e.target.value })}
          placeholder={adapter.base_url_default ?? "https://…"}
          data-testid="input-profile-base-url"
          className="mt-1 w-full rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono text-text"
        />
      </label>

      {adapter.secrets.map((s) => (
        <label key={s.key} className="block">
          <span className="text-xs text-text-faint">
            {s.label} — env var name {s.required ? "" : "(optional)"}
          </span>
          <input
            value={form.secret_refs[s.key] ?? ""}
            onChange={(e) =>
              setForm({
                ...form,
                secret_refs: { ...form.secret_refs, [s.key]: e.target.value },
              })
            }
            placeholder={s.env}
            data-testid={`input-secret-${s.key}`}
            className="mt-1 w-full rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono text-text"
          />
        </label>
      ))}

      <p className="text-[11px] text-text-faint">
        Enter the <em>name</em> of an environment variable, not the secret itself. The value is read
        server-side at connection time and never stored or shown here.
      </p>

      <label className="flex items-center gap-2 text-sm text-text">
        <input
          type="checkbox"
          checked={form.enabled}
          onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
          data-testid="input-profile-enabled"
        />
        Enable for runtime capability resolution
      </label>

      {errors.length > 0 && (
        <ul className="text-[11px] text-error list-disc list-inside" data-testid="form-errors">
          {errors.map((e) => (
            <li key={e}>{e}</li>
          ))}
        </ul>
      )}

      <button
        onClick={submit}
        disabled={saving || errors.length > 0}
        data-testid="button-save-profile"
        className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-hover transition disabled:opacity-40"
      >
        Save profile
      </button>
    </div>
  );
}

function ProfileRow({
  profile,
  onChanged,
}: {
  profile: Profile;
  onChanged: () => void;
}) {
  const { push } = useToast();
  const [probe, setProbe] = useState<ProbeResult | null>(null);
  const [busy, setBusy] = useState(false);

  const test = async () => {
    setBusy(true);
    try {
      setProbe(
        await apiFetch<ProbeResult>(`/integrations/profiles/${profile.id}/test`, {
          method: "POST",
        }),
      );
    } catch (e) {
      push({ tone: "error", title: "Test failed", description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const toggle = async () => {
    setBusy(true);
    try {
      await apiFetch(`/integrations/profiles/${profile.id}`, {
        method: "PATCH",
        body: JSON.stringify({ enabled: !profile.enabled }),
      });
      onChanged();
    } catch (e) {
      push({ tone: "error", title: "Could not update", description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    setBusy(true);
    try {
      await apiFetch(`/integrations/profiles/${profile.id}`, { method: "DELETE" });
      push({ tone: "info", title: `Deleted ${profile.name}` });
      onChanged();
    } catch (e) {
      push({ tone: "error", title: "Could not delete", description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const meta = probe ? probeStateMeta(probe.state) : null;

  return (
    <div
      className="border border-border bg-bg rounded-md p-3 flex flex-col gap-2"
      data-testid={`profile-row-${profile.id}`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-sm font-medium text-text truncate">{profile.name}</span>
          <span className="text-[10px] uppercase tracking-wider text-text-faint">
            {profile.adapter_id}
          </span>
          {profile.enabled ? (
            <span className="text-[10px] rounded-full px-1.5 py-0.5 bg-success/15 text-success">
              enabled
            </span>
          ) : (
            <span className="text-[10px] rounded-full px-1.5 py-0.5 bg-surface-alt text-text-muted">
              disabled
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={test}
            disabled={busy}
            data-testid={`button-test-${profile.id}`}
            className="inline-flex items-center gap-1 rounded-md bg-surface-alt px-2 py-1 text-[11px] text-text hover:bg-border transition disabled:opacity-40"
          >
            <RefreshCw className={`w-3 h-3 ${busy ? "animate-spin" : ""}`} />
            Test
          </button>
          <button
            onClick={toggle}
            disabled={busy}
            data-testid={`button-toggle-${profile.id}`}
            className="rounded-md bg-surface-alt px-2 py-1 text-[11px] text-text hover:bg-border transition disabled:opacity-40"
          >
            {profile.enabled ? "Disable" : "Enable"}
          </button>
          <button
            onClick={remove}
            disabled={busy}
            data-testid={`button-delete-${profile.id}`}
            className="rounded-md bg-surface-alt px-2 py-1 text-[11px] text-error hover:bg-border transition disabled:opacity-40"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap text-[11px] text-text-faint">
        {profile.capabilities.map((c) => (
          <span key={c} className="rounded bg-surface-alt px-1.5 py-0.5">
            {c}
          </span>
        ))}
        {profile.secret_refs.map((r) => (
          <span key={r.key} className="font-mono">
            {r.env ?? r.key}:{r.present ? "set" : "missing"}
          </span>
        ))}
      </div>

      {meta && (
        <div className="text-[11px]" data-testid={`probe-result-${profile.id}`}>
          <span className={meta.className}>{meta.label}</span>
          {probe?.latency_ms != null && (
            <span className="text-text-faint"> · {probe.latency_ms} ms</span>
          )}
          {probe?.detail && <span className="text-text-faint"> · {probe.detail}</span>}
        </div>
      )}
    </div>
  );
}

export default function IntegrationsManager() {
  const [adapters, setAdapters] = useState<Adapter[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const loadProfiles = () => {
    apiFetch<Profile[]>("/integrations/profiles")
      .then(setProfiles)
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    apiFetch<Adapter[]>("/integrations/adapters")
      .then((a) => {
        setAdapters(a);
        if (a.length > 0) setSelected(a[0].id);
      })
      .catch((e) => setError(String(e)));
    loadProfiles();
  }, []);

  const current = adapters.find((a) => a.id === selected);

  return (
    <section
      className="rounded-lg border border-border bg-surface p-6 space-y-4"
      data-testid="panel-integrations"
    >
      <div className="flex items-center gap-2">
        <Plug className="w-4 h-4 text-primary" />
        <h2 className="font-semibold text-text">Integrations — connect an adapter</h2>
      </div>
      <p className="text-sm text-text-muted">
        Configure any catalogued provider with a connection profile: pick an adapter, point it at
        your endpoint, reference secrets by environment-variable name, then run a health probe.
        Enabled profiles are exposed to agents via capability resolution.
      </p>

      {error && (
        <div className="text-error text-xs" data-testid="integrations-error">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <label className="block">
            <span className="text-xs text-text-faint">Adapter</span>
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              data-testid="select-adapter"
              className="mt-1 w-full rounded-md border border-border bg-bg px-2 py-1.5 text-sm text-text"
            >
              {adapters.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} — {a.category}
                </option>
              ))}
            </select>
          </label>
          {current && <CreateForm adapter={current} onCreated={loadProfiles} />}
        </div>

        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-text-faint uppercase tracking-wider">
            Configured profiles ({profiles.length})
          </h3>
          {profiles.length === 0 ? (
            <div className="text-xs text-text-muted" data-testid="no-profiles">
              No profiles yet. Create one on the left.
            </div>
          ) : (
            <div className="space-y-2">
              {profiles.map((p) => (
                <ProfileRow key={p.id} profile={p} onChanged={loadProfiles} />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
