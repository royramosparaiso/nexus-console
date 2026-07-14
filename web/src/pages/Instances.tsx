import { useEffect, useState } from "react";
import { Link } from "wouter";
import { apiFetch } from "@/lib/api";
import { Plus } from "lucide-react";

type Instance = {
  instance_id: string;
  name: string;
  persona_display_name: string;
  modality: string;
  endpoint: string | null;
  version: string | null;
  status: string;
  created_at: string;
};

export default function Instances() {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    apiFetch<Instance[]>("/instances")
      .then((data) => {
        setInstances(data);
        setError(null);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
    // Refresh when a deploy or other instance mutation completes anywhere in
    // the app. Broadcast via CustomEvent so we don't need a store.
    const handler = () => refresh();
    window.addEventListener("nexus:instance-updated", handler);
    return () => window.removeEventListener("nexus:instance-updated", handler);
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
            Instances
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Nexus Platform instances managed by this Console.
          </p>
        </div>
        <Link
          href="/wizard"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-bg text-sm font-medium hover:bg-primary-hover transition-colors"
          data-testid="button-new-instance"
        >
          <Plus className="w-4 h-4" />
          New instance
        </Link>
      </header>

      {loading && (
        <div className="text-text-muted text-sm" data-testid="text-loading">
          Loading…
        </div>
      )}
      {error && (
        <div className="text-error text-sm" data-testid="text-error">
          {error}
        </div>
      )}
      {!loading && !error && instances.length === 0 && (
        <div
          className="border border-dashed border-border rounded-lg p-12 text-center"
          data-testid="empty-instances"
        >
          <h2 className="text-lg font-medium text-text">No instances yet</h2>
          <p className="text-sm text-text-muted mt-2 max-w-md mx-auto">
            Launch the wizard to create your first Nexus Platform instance. In local mode, the Console
            deploys a Platform to a Docker container on the same host.
          </p>
        </div>
      )}

      {instances.length > 0 && (
        <div className="grid gap-3">
          {instances.map((i) => (
            <div
              key={i.instance_id}
              className="border border-border bg-surface rounded-lg p-4 flex items-center justify-between"
              data-testid={`card-instance-${i.instance_id}`}
            >
              <div>
                <div className="font-medium text-text">{i.name}</div>
                <div className="text-xs text-text-muted mt-1">
                  {i.persona_display_name} · {i.modality} · {i.status}
                </div>
              </div>
              {i.endpoint && (
                <a
                  href={i.endpoint}
                  target="_blank"
                  rel="noreferrer"
                  className="text-primary text-sm hover:underline"
                >
                  Open
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
