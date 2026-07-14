/**
 * Global toast provider.
 *
 * Any component below <ToastProvider> can call `useToast()` and push messages
 * with tone=success|error|info. Toasts stack in the bottom-right corner and
 * auto-dismiss after `duration` ms (default 5s). This is intentionally tiny —
 * no library, no animations that need a compositor thread. Enough for a
 * console UI.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { PropsWithChildren, ReactNode } from "react";

export type ToastTone = "success" | "error" | "info";

export interface Toast {
  id: string;
  tone: ToastTone;
  title: string;
  description?: ReactNode;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  push: (t: Omit<Toast, "id">) => string;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used inside a <ToastProvider>");
  }
  return ctx;
}

/**
 * Non-throwing variant for components that want to opt into toasts if they're
 * available but keep working (silently) if not. Handy for shared components
 * rendered outside the provider (tests, stubs).
 */
export function useOptionalToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (ctx) return ctx;
  return {
    toasts: [],
    push: () => "",
    dismiss: () => {
      /* no-op */
    },
  };
}

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const push = useCallback<ToastContextValue["push"]>(
    (t) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
      const duration = t.duration ?? 5_000;
      setToasts((prev) => [...prev, { ...t, id }]);
      if (duration > 0) {
        const timer = setTimeout(() => dismiss(id), duration);
        timers.current.set(id, timer);
      }
      return id;
    },
    [dismiss],
  );

  useEffect(
    () => () => {
      // On unmount, clear any pending timers.
      timers.current.forEach((t) => clearTimeout(t));
      timers.current.clear();
    },
    [],
  );

  const value = useMemo<ToastContextValue>(
    () => ({ toasts, push, dismiss }),
    [toasts, push, dismiss],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

interface ViewportProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

function ToastViewport({ toasts, onDismiss }: ViewportProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      data-testid="toast-viewport"
      className="fixed bottom-4 right-4 z-[9999] flex w-96 max-w-[calc(100vw-2rem)] flex-col gap-2"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map((t) => (
        <ToastCard key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastCard({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const toneStyles: Record<ToastTone, { border: string; badge: string; label: string }> = {
    success: {
      border: "border-l-primary",
      badge: "bg-primary/15 text-primary",
      label: "Success",
    },
    error: {
      border: "border-l-error",
      badge: "bg-error/15 text-error",
      label: "Error",
    },
    info: {
      border: "border-l-text-muted",
      badge: "bg-surface-alt text-text-muted",
      label: "Info",
    },
  };
  const s = toneStyles[toast.tone];

  return (
    <div
      data-testid={`toast-${toast.tone}`}
      role="status"
      aria-live="polite"
      className={`pointer-events-auto flex items-start gap-3 rounded-md border border-border ${s.border} border-l-4 bg-surface px-4 py-3 shadow-lg`}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-mono uppercase ${s.badge}`}>
            {s.label}
          </span>
          <span data-testid="toast-title" className="text-sm font-semibold text-text truncate">
            {toast.title}
          </span>
        </div>
        {toast.description && (
          <div data-testid="toast-description" className="mt-1 text-sm text-text-muted break-words">
            {toast.description}
          </div>
        )}
      </div>
      <button
        type="button"
        aria-label="Dismiss"
        data-testid="button-dismiss-toast"
        onClick={() => onDismiss(toast.id)}
        className="text-text-muted hover:text-text transition-colors"
      >
        ×
      </button>
    </div>
  );
}
