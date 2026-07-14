/**
 * ecosystem.ts — types + pure helpers for the AI-ecosystem registry served by
 * the Console backend at GET /ecosystem. Kept framework-free so the status
 * mapping and ordering logic are unit-testable without React.
 */

export type EcosystemStatus =
  | "available"
  | "configurable"
  | "experimental"
  | "planned";

export type EcosystemIntegration = "native" | "external" | "catalog";

export interface EcosystemEntry {
  id: string;
  name: string;
  category: string;
  status: EcosystemStatus;
  integration: EcosystemIntegration;
  summary: string;
  provider: string | null;
  requires: string[];
  docs_url: string | null;
  tags: string[];
  template_id: string | null;
}

export interface CategoryGroup {
  category: string;
  label: string;
  entries: EcosystemEntry[];
}

export interface EcosystemView {
  version: string;
  counts: Record<string, number>;
  groups: CategoryGroup[];
}

export interface StatusMeta {
  label: string;
  /** Tailwind classes using the existing design tokens. */
  className: string;
  /** Short honest description of what the status means. */
  hint: string;
}

const STATUS_META: Record<EcosystemStatus, StatusMeta> = {
  available: {
    label: "Available",
    className: "bg-success/15 text-success",
    hint: "Works today with what ships in this repo — no extra setup.",
  },
  configurable: {
    label: "Configurable",
    className: "bg-primary/15 text-primary",
    hint: "Supported, but needs an endpoint, key, or flag before it does anything.",
  },
  experimental: {
    label: "Experimental",
    className: "bg-warning/15 text-warning",
    hint: "Real code exists but is early / behind a flag — not production-hardened.",
  },
  planned: {
    label: "Planned",
    className: "bg-surface-alt text-text-muted",
    hint: "Discoverable catalogue entry only. No integration code yet.",
  },
};

export function statusMeta(status: EcosystemStatus): StatusMeta {
  return STATUS_META[status] ?? STATUS_META.planned;
}

export const INTEGRATION_LABEL: Record<EcosystemIntegration, string> = {
  native: "Native",
  external: "External",
  catalog: "Catalogue",
};

/** Total entries across all groups. */
export function totalEntries(view: EcosystemView): number {
  return view.groups.reduce((n, g) => n + g.entries.length, 0);
}

/**
 * Order used for the status summary chips — most "done" first so the honest
 * distribution (lots of planned, few available) reads left-to-right.
 */
export const STATUS_ORDER: EcosystemStatus[] = [
  "available",
  "configurable",
  "experimental",
  "planned",
];
