import { useEffect, useMemo, useState } from "react";
import { Bot, Cog, Puzzle, Search, X } from "lucide-react";
import { apiFetch } from "../lib/api";

// ---------- Types ----------

type ArtifactType = "agent" | "sidecar" | "skill";

type Card = {
  id: string;
  name: string;
  artifact_type: ArtifactType;
  lifecycle: "project" | "ops" | "both" | "none";
  category: string;
  phase: number | null;
  step: number | null;
  domain: string | null;
  rollout_stage: string | null;
  autonomy: string | null;
  maturity: number | null;
  verticals: string[];
  role: string | null;
  mode: string | null;
  depends_on: string[];
  produces: string | null;
  tools: string[];
  tags: string[];
  gate: boolean;
  optional: boolean;
  path: string;
};

type Catalog = {
  version: string;
  total: number;
  cards: Card[];
  indexes: {
    by_category: Record<string, string[]>;
    by_domain: Record<string, string[]>;
    by_rollout_stage: Record<string, string[]>;
    by_autonomy: Record<string, string[]>;
    by_artifact_type: Record<string, string[]>;
    by_role: Record<string, string[]>;
    by_tag: Record<string, string[]>;
    by_verticals: Record<string, string[]>;
    by_lifecycle: Record<string, string[]>;
  };
  enums: {
    artifact_type: string[];
    lifecycle: string[];
    rollout_stage: string[];
    autonomy: string[];
    ops_domains: string[];
    lifecycle_categories: string[];
    verticals: string[];
  };
};

type Detail = { card: Card; body: string };

// ---------- Icons + badges ----------

function ArtifactIcon({ kind }: { kind: ArtifactType }) {
  const Icon = kind === "agent" ? Bot : kind === "sidecar" ? Cog : Puzzle;
  const cls =
    kind === "agent"
      ? "text-primary"
      : kind === "sidecar"
        ? "text-warning"
        : "text-success";
  return <Icon className={`w-4 h-4 ${cls}`} />;
}

function Badge({
  children,
  tone = "neutral",
  onClick,
  active = false,
}: {
  children: React.ReactNode;
  tone?: "neutral" | "primary" | "warning" | "success" | "error";
  onClick?: () => void;
  active?: boolean;
}) {
  const tones: Record<string, string> = {
    neutral: "bg-surface-alt text-text-muted border-border",
    primary: "bg-primary/10 text-primary border-primary/30",
    warning: "bg-warning/10 text-warning border-warning/30",
    success: "bg-success/10 text-success border-success/30",
    error: "bg-error/10 text-error border-error/30",
  };
  const base =
    "inline-flex items-center gap-1 px-2 py-0.5 text-[11px] leading-4 font-medium border rounded";
  const activeCls = active ? " ring-1 ring-primary" : "";
  if (onClick) {
    return (
      <button onClick={onClick} className={`${base} ${tones[tone]}${activeCls} hover:opacity-80`}>
        {children}
      </button>
    );
  }
  return <span className={`${base} ${tones[tone]}${activeCls}`}>{children}</span>;
}

// ---------- Filter chip group ----------

function FilterGroup({
  label,
  options,
  selected,
  onToggle,
  counts,
}: {
  label: string;
  options: string[];
  selected: Set<string>;
  onToggle: (v: string) => void;
  counts?: Record<string, number>;
}) {
  if (options.length === 0) return null;
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wide text-text-muted font-semibold mb-2">
        {label}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => {
          const isActive = selected.has(opt);
          const count = counts?.[opt];
          return (
            <button
              key={opt}
              onClick={() => onToggle(opt)}
              data-testid={`filter-${label.toLowerCase()}-${opt}`}
              className={`px-2 py-1 text-[11px] font-medium border rounded transition-colors ${
                isActive
                  ? "bg-primary text-white border-primary"
                  : "bg-surface text-text-muted border-border hover:border-primary/50 hover:text-text"
              }`}
            >
              {opt}
              {count !== undefined && (
                <span className={`ml-1 ${isActive ? "opacity-80" : "opacity-60"}`}>
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Card list item ----------

function CardRow({
  card,
  active,
  onClick,
}: {
  card: Card;
  active: boolean;
  onClick: () => void;
}) {
  const tone =
    card.artifact_type === "agent"
      ? "primary"
      : card.artifact_type === "sidecar"
        ? "warning"
        : "success";
  return (
    <button
      onClick={onClick}
      data-testid={`card-${card.id}`}
      className={`w-full text-left border rounded-lg p-3 hover:border-primary/50 transition-colors ${
        active ? "border-primary bg-surface-alt" : "border-border bg-surface"
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <ArtifactIcon kind={card.artifact_type} />
          <span className="font-mono text-sm text-text truncate">{card.id}</span>
        </div>
        <Badge tone={tone as "primary" | "warning" | "success"}>{card.artifact_type}</Badge>
      </div>
      <div className="flex flex-wrap gap-1 mb-1.5">
        {card.domain && <Badge>{card.domain}</Badge>}
        {card.rollout_stage && <Badge>{card.rollout_stage}</Badge>}
        {card.autonomy && <Badge>{card.autonomy}</Badge>}
        {card.category && card.lifecycle === "project" && <Badge>{card.category}</Badge>}
        {card.gate && <Badge tone="error">gate</Badge>}
        {card.optional && <Badge tone="neutral">optional</Badge>}
      </div>
      <div className="text-[11px] text-text-muted line-clamp-1">
        {card.role && <span>{card.role}</span>}
        {card.role && card.mode && <span> · </span>}
        {card.mode && <span>{card.mode}</span>}
        {card.produces && (
          <>
            <span> → </span>
            <span>{card.produces}</span>
          </>
        )}
      </div>
    </button>
  );
}

// ---------- Detail panel ----------

function DetailPanel({
  cardId,
  onClose,
}: {
  cardId: string;
  onClose: () => void;
}) {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setDetail(null);
    setError(null);
    apiFetch<Detail>(`/agent-templates/${cardId}`)
      .then(setDetail)
      .catch((e) => setError(String(e)));
  }, [cardId]);

  return (
    <div
      className="border border-border bg-surface rounded-lg overflow-hidden flex flex-col"
      data-testid="detail-panel"
    >
      <div className="flex items-center justify-between p-3 border-b border-border">
        <div className="flex items-center gap-2 min-w-0">
          {detail && <ArtifactIcon kind={detail.card.artifact_type} />}
          <span className="font-mono text-sm text-text truncate" data-testid="detail-id">
            {cardId}
          </span>
        </div>
        <button
          onClick={onClose}
          data-testid="button-close-detail"
          className="text-text-muted hover:text-text p-1"
          aria-label="Close detail"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="overflow-auto p-4 flex-1">
        {error && <div className="text-error text-sm">{error}</div>}
        {!detail && !error && <div className="text-text-muted text-sm">Loading…</div>}
        {detail && (
          <>
            <div className="mb-4 grid grid-cols-2 gap-y-1.5 gap-x-4 text-xs">
              <div className="text-text-muted">artifact_type</div>
              <div className="font-mono text-text">{detail.card.artifact_type}</div>
              <div className="text-text-muted">lifecycle</div>
              <div className="font-mono text-text">{detail.card.lifecycle}</div>
              {detail.card.domain && (
                <>
                  <div className="text-text-muted">domain</div>
                  <div className="font-mono text-text">{detail.card.domain}</div>
                </>
              )}
              {detail.card.rollout_stage && (
                <>
                  <div className="text-text-muted">rollout_stage</div>
                  <div className="font-mono text-text">{detail.card.rollout_stage}</div>
                </>
              )}
              {detail.card.autonomy && (
                <>
                  <div className="text-text-muted">autonomy</div>
                  <div className="font-mono text-text">{detail.card.autonomy}</div>
                </>
              )}
              {detail.card.role && (
                <>
                  <div className="text-text-muted">role</div>
                  <div className="font-mono text-text">{detail.card.role}</div>
                </>
              )}
              {detail.card.mode && (
                <>
                  <div className="text-text-muted">mode</div>
                  <div className="font-mono text-text">{detail.card.mode}</div>
                </>
              )}
              {detail.card.produces && (
                <>
                  <div className="text-text-muted">produces</div>
                  <div className="font-mono text-text">{detail.card.produces}</div>
                </>
              )}
              {detail.card.tools.length > 0 && (
                <>
                  <div className="text-text-muted">tools</div>
                  <div className="font-mono text-text break-all">
                    {detail.card.tools.join(", ")}
                  </div>
                </>
              )}
              {detail.card.verticals.length > 0 && (
                <>
                  <div className="text-text-muted">verticals</div>
                  <div className="font-mono text-text">{detail.card.verticals.join(", ")}</div>
                </>
              )}
              {detail.card.tags.length > 0 && (
                <>
                  <div className="text-text-muted">tags</div>
                  <div className="flex flex-wrap gap-1">
                    {detail.card.tags.map((t) => (
                      <Badge key={t}>{t}</Badge>
                    ))}
                  </div>
                </>
              )}
            </div>
            <pre className="whitespace-pre-wrap break-words text-xs font-mono text-text-muted bg-surface-alt border border-border rounded p-3">
              {detail.body}
            </pre>
          </>
        )}
      </div>
    </div>
  );
}

// ---------- Main page ----------

export default function Agents() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selArtifact, setSelArtifact] = useState<Set<string>>(new Set());
  const [selLifecycle, setSelLifecycle] = useState<Set<string>>(new Set());
  const [selDomain, setSelDomain] = useState<Set<string>>(new Set());
  const [selRollout, setSelRollout] = useState<Set<string>>(new Set());
  const [selAutonomy, setSelAutonomy] = useState<Set<string>>(new Set());
  const [selCategory, setSelCategory] = useState<Set<string>>(new Set());
  const [selRole, setSelRole] = useState<Set<string>>(new Set());
  const [selVertical, setSelVertical] = useState<Set<string>>(new Set());
  const [selTag, setSelTag] = useState<Set<string>>(new Set());
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Catalog>("/agent-templates")
      .then(setCatalog)
      .catch((e) => setLoadError(String(e)));
  }, []);

  const toggle =
    (setFn: React.Dispatch<React.SetStateAction<Set<string>>>) => (v: string) => {
      setFn((prev) => {
        const next = new Set(prev);
        if (next.has(v)) next.delete(v);
        else next.add(v);
        return next;
      });
    };

  const clearAll = () => {
    setSearch("");
    setSelArtifact(new Set());
    setSelLifecycle(new Set());
    setSelDomain(new Set());
    setSelRollout(new Set());
    setSelAutonomy(new Set());
    setSelCategory(new Set());
    setSelRole(new Set());
    setSelVertical(new Set());
    setSelTag(new Set());
  };

  const matches = (c: Card): boolean => {
    if (selArtifact.size && !selArtifact.has(c.artifact_type)) return false;
    if (selLifecycle.size && !selLifecycle.has(c.lifecycle)) return false;
    if (selDomain.size && (!c.domain || !selDomain.has(c.domain))) return false;
    if (selRollout.size && (!c.rollout_stage || !selRollout.has(c.rollout_stage))) return false;
    if (selAutonomy.size && (!c.autonomy || !selAutonomy.has(c.autonomy))) return false;
    if (selCategory.size && !selCategory.has(c.category)) return false;
    if (selRole.size && (!c.role || !selRole.has(c.role))) return false;
    if (selVertical.size && !c.verticals.some((v) => selVertical.has(v))) return false;
    if (selTag.size && !c.tags.some((t) => selTag.has(t))) return false;
    if (search.trim()) {
      const needle = search.toLowerCase().trim();
      const hay = [
        c.id,
        c.produces ?? "",
        c.role ?? "",
        c.domain ?? "",
        c.category,
        ...c.tags,
        ...c.tools,
      ]
        .join(" ")
        .toLowerCase();
      if (!hay.includes(needle)) return false;
    }
    return true;
  };

  const filtered = useMemo(() => (catalog ? catalog.cards.filter(matches) : []), [
    catalog,
    search,
    selArtifact,
    selLifecycle,
    selDomain,
    selRollout,
    selAutonomy,
    selCategory,
    selRole,
    selVertical,
    selTag,
  ]);

  const topTags = useMemo(() => {
    if (!catalog) return [];
    const entries = Object.entries(catalog.indexes.by_tag);
    entries.sort((a, b) => b[1].length - a[1].length);
    return entries.slice(0, 24).map(([k]) => k);
  }, [catalog]);

  const anyFilter =
    !!search ||
    selArtifact.size +
      selLifecycle.size +
      selDomain.size +
      selRollout.size +
      selAutonomy.size +
      selCategory.size +
      selRole.size +
      selVertical.size +
      selTag.size >
      0;

  if (loadError) {
    return (
      <div className="p-8">
        <div className="text-error text-sm" data-testid="text-load-error">
          Failed to load agent catalogue: {loadError}
        </div>
      </div>
    );
  }

  if (!catalog) {
    return (
      <div className="p-8">
        <div className="text-text-muted text-sm">Loading agent catalogue…</div>
      </div>
    );
  }

  const countsFor = (idx: Record<string, string[]>): Record<string, number> => {
    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(idx)) out[k] = v.length;
    return out;
  };

  return (
    <div className="flex h-full">
      {/* Sidebar filters */}
      <aside className="w-72 shrink-0 border-r border-border bg-surface p-4 overflow-auto space-y-5">
        <div>
          <div className="text-[11px] uppercase tracking-wide text-text-muted font-semibold mb-2">
            Search
          </div>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2 top-1/2 -translate-y-1/2 text-text-faint" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="id, tag, tool, role…"
              data-testid="input-search"
              className="w-full pl-8 pr-2 py-1.5 text-sm bg-bg border border-border rounded focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <FilterGroup
          label="Artifact"
          options={catalog.enums.artifact_type}
          selected={selArtifact}
          onToggle={toggle(setSelArtifact)}
          counts={countsFor(catalog.indexes.by_artifact_type)}
        />

        <FilterGroup
          label="Lifecycle"
          options={catalog.enums.lifecycle}
          selected={selLifecycle}
          onToggle={toggle(setSelLifecycle)}
          counts={countsFor(catalog.indexes.by_lifecycle)}
        />

        <FilterGroup
          label="Domain"
          options={catalog.enums.ops_domains}
          selected={selDomain}
          onToggle={toggle(setSelDomain)}
          counts={countsFor(catalog.indexes.by_domain)}
        />

        <FilterGroup
          label="Rollout"
          options={catalog.enums.rollout_stage}
          selected={selRollout}
          onToggle={toggle(setSelRollout)}
          counts={countsFor(catalog.indexes.by_rollout_stage)}
        />

        <FilterGroup
          label="Autonomy"
          options={catalog.enums.autonomy}
          selected={selAutonomy}
          onToggle={toggle(setSelAutonomy)}
          counts={countsFor(catalog.indexes.by_autonomy)}
        />

        <FilterGroup
          label="Category"
          options={catalog.enums.lifecycle_categories}
          selected={selCategory}
          onToggle={toggle(setSelCategory)}
          counts={countsFor(catalog.indexes.by_category)}
        />

        <FilterGroup
          label="Role"
          options={Object.keys(catalog.indexes.by_role).sort()}
          selected={selRole}
          onToggle={toggle(setSelRole)}
          counts={countsFor(catalog.indexes.by_role)}
        />

        <FilterGroup
          label="Vertical"
          options={catalog.enums.verticals}
          selected={selVertical}
          onToggle={toggle(setSelVertical)}
          counts={countsFor(catalog.indexes.by_verticals)}
        />

        <FilterGroup
          label="Tag"
          options={topTags}
          selected={selTag}
          onToggle={toggle(setSelTag)}
          counts={countsFor(catalog.indexes.by_tag)}
        />

        {anyFilter && (
          <button
            onClick={clearAll}
            data-testid="button-clear-filters"
            className="w-full py-1.5 text-xs border border-border rounded text-text-muted hover:text-text hover:border-primary/50"
          >
            Clear all filters
          </button>
        )}
      </aside>

      {/* Results */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="border-b border-border bg-surface px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
              Agent Factory
            </h1>
            <p className="text-xs text-text-muted mt-0.5">
              Catalogue v{catalog.version} · {catalog.total} cards · showing{" "}
              <span data-testid="text-result-count">{filtered.length}</span>
            </p>
          </div>
        </header>

        <div className="flex-1 flex min-h-0">
          <div className="flex-1 overflow-auto p-4">
            {filtered.length === 0 ? (
              <div className="border border-dashed border-border rounded-lg p-12 text-center">
                <p className="text-sm text-text-muted">No cards match the current filters.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filtered.map((c) => (
                  <CardRow
                    key={c.id}
                    card={c}
                    active={activeId === c.id}
                    onClick={() => setActiveId(c.id)}
                  />
                ))}
              </div>
            )}
          </div>
          {activeId && (
            <div className="w-[420px] shrink-0 border-l border-border p-3 overflow-hidden">
              <DetailPanel cardId={activeId} onClose={() => setActiveId(null)} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
