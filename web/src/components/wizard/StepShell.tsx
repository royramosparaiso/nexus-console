import type { ReactNode } from "react";

type Props = {
  index: number;
  total: number;
  title: string;
  description?: string;
  children: ReactNode;
};

export default function StepShell({ index, total, title, description, children }: Props) {
  return (
    <section
      className="border border-border bg-surface rounded-lg p-6 space-y-5"
      data-testid={`step-${index}`}
    >
      <header>
        <div className="text-xs uppercase tracking-wider text-text-faint mb-1">
          Step {index} of {total}
        </div>
        <h2 className="text-lg font-semibold text-text" data-testid={`step-${index}-title`}>
          {title}
        </h2>
        {description && (
          <p className="text-sm text-text-muted mt-1">{description}</p>
        )}
      </header>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

export function Field({
  label,
  hint,
  children,
  testid,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
  testid?: string;
}) {
  return (
    <label className="block space-y-1.5" data-testid={testid}>
      <span className="text-sm font-medium text-text">{label}</span>
      {children}
      {hint && <span className="block text-xs text-text-muted">{hint}</span>}
    </label>
  );
}

export const inputCls =
  "w-full bg-surface-alt border border-border rounded-md px-3 py-2 text-sm text-text placeholder:text-text-faint focus:outline-none focus:border-primary transition-colors";
