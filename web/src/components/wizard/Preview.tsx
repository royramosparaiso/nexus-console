import type { WizardPreview } from "@/lib/wizardTypes";
import { AlertTriangle } from "lucide-react";

type Props = {
  data: WizardPreview | null;
  loading: boolean;
  error: string | null;
};

export default function Preview({ data, loading, error }: Props) {
  return (
    <section
      className="border border-border bg-surface rounded-lg p-6 space-y-4"
      data-testid="preview-panel"
    >
      <header>
        <h2 className="text-lg font-semibold text-text">Preview</h2>
        <p className="text-sm text-text-muted mt-1">
          Live rendering of <code className="text-xs bg-surface-alt px-1 py-0.5 rounded">nexus.instance.yaml</code>.
        </p>
      </header>
      {loading && (
        <div className="text-sm text-text-muted" data-testid="preview-loading">Rendering…</div>
      )}
      {error && (
        <div className="text-sm text-error" data-testid="preview-error">{error}</div>
      )}
      {data?.warnings && data.warnings.length > 0 && (
        <ul className="space-y-2" data-testid="preview-warnings">
          {data.warnings.map((w, i) => (
            <li
              key={i}
              className="flex items-start gap-2 text-xs text-warning bg-surface-alt border border-border rounded-md p-2"
              data-testid={`warning-${i}`}
            >
              <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span>{w}</span>
            </li>
          ))}
        </ul>
      )}
      {data && (
        <pre
          className="text-xs font-mono bg-surface-alt border border-border rounded-md p-3 overflow-auto max-h-[600px] text-text"
          data-testid="preview-yaml"
        >
{data.yaml}
        </pre>
      )}
    </section>
  );
}
