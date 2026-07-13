import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { CheckCircle2, Circle } from "lucide-react";

type Provider = {
  provider: string;
  configured: boolean;
  models: string[];
};

export default function Providers() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Provider[]>("/providers")
      .then((data) => {
        setProviders(data);
        setError(null);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          LLM Providers
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Configure model providers once here. Console syncs credentials to selected instances via signed
          <code className="mx-1 text-xs bg-surface-alt px-1 py-0.5 rounded">set_llm_provider</code>
          commands.
        </p>
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {providers.map((p) => (
          <div
            key={p.provider}
            className="border border-border bg-surface rounded-lg p-4"
            data-testid={`card-provider-${p.provider}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {p.configured ? (
                  <CheckCircle2 className="w-4 h-4 text-success" />
                ) : (
                  <Circle className="w-4 h-4 text-text-faint" />
                )}
                <span className="font-medium capitalize text-text">{p.provider}</span>
              </div>
              <button
                className="text-xs text-primary hover:underline"
                data-testid={`button-configure-${p.provider}`}
              >
                {p.configured ? "Update" : "Configure"}
              </button>
            </div>
            {p.models.length > 0 && (
              <div className="text-xs text-text-muted">{p.models.join(" · ")}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
