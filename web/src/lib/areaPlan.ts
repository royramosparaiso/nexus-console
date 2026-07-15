/**
 * Deployment area-plan reconciliation.
 *
 * When the operator selects agent templates to deploy, the backend proposes an
 * area/department for each (see `POST /agent-templates/recommend-areas`). The
 * UI then keeps a per-agent *plan* that the operator can edit. This module owns
 * the pure reconciliation rules so they can be unit-tested independently of
 * React:
 *
 *  - auto-fill only newly-selected / still-unassigned agents from the proposals
 *  - never overwrite an area the operator set manually
 *  - drop entries for agents that were deselected (no stale recommendations)
 *
 * The `null` area is a first-class value meaning "unassigned" — allowed at
 * deploy time.
 */

export type RecommendationSource =
  | "template_default"
  | "tag_match"
  | "domain_match"
  | "fallback";

export interface AreaRecommendation {
  template_id: string;
  artifact_type: string | null;
  area_slug: string | null;
  area_label: string | null;
  source: RecommendationSource;
  rationale: string;
  candidates: string[];
}

export interface AreaOption {
  slug: string;
  label: string;
  tier: string;
}

export interface RecommendResponse {
  recommendations: AreaRecommendation[];
  areas: AreaOption[];
  unknown_template_ids: string[];
}

/** One row in the editable plan. */
export interface PlanEntry {
  templateId: string;
  /** Chosen area slug, or null when unassigned. */
  areaSlug: string | null;
  /** The originally recommended area (for the "reset to suggestion" affordance). */
  recommendedSlug: string | null;
  source: RecommendationSource;
  rationale: string;
  candidates: string[];
  /** True once the operator has hand-picked the area for this agent. */
  manual: boolean;
}

function toEntry(rec: AreaRecommendation): PlanEntry {
  return {
    templateId: rec.template_id,
    areaSlug: rec.area_slug,
    recommendedSlug: rec.area_slug,
    source: rec.source,
    rationale: rec.rationale,
    candidates: rec.candidates,
    manual: false,
  };
}

/**
 * Merge fresh recommendations into an existing plan.
 *
 * `selectedIds` is the authoritative current selection (order preserved). For
 * each selected id:
 *   - if there is a prior manual entry, keep the operator's choice but refresh
 *     the recommendation metadata (rationale/candidates) from `recs`;
 *   - otherwise adopt the recommendation (auto-fill).
 * Entries whose id is no longer selected are dropped.
 */
export function reconcilePlan(
  prev: PlanEntry[],
  recs: AreaRecommendation[],
  selectedIds: string[],
): PlanEntry[] {
  const prevById = new Map(prev.map((e) => [e.templateId, e]));
  const recById = new Map(recs.map((r) => [r.template_id, r]));

  const out: PlanEntry[] = [];
  for (const id of selectedIds) {
    const rec = recById.get(id);
    const existing = prevById.get(id);

    if (existing && existing.manual) {
      // Preserve the manual choice; refresh advisory metadata if we have it.
      out.push(
        rec
          ? {
              ...existing,
              recommendedSlug: rec.area_slug,
              source: rec.source,
              rationale: rec.rationale,
              candidates: rec.candidates,
            }
          : existing,
      );
      continue;
    }

    if (rec) {
      out.push(toEntry(rec));
    } else if (existing) {
      // No fresh recommendation (e.g. recs not loaded yet) — keep what we had.
      out.push(existing);
    } else {
      // Selected but no recommendation available: unassigned fallback.
      out.push({
        templateId: id,
        areaSlug: null,
        recommendedSlug: null,
        source: "fallback",
        rationale: "No recommendation available — assign an area manually.",
        candidates: [],
        manual: false,
      });
    }
  }
  return out;
}

/** Apply a manual area choice to one agent, marking it as operator-set. */
export function setAreaManually(
  plan: PlanEntry[],
  templateId: string,
  areaSlug: string | null,
): PlanEntry[] {
  return plan.map((e) =>
    e.templateId === templateId ? { ...e, areaSlug, manual: true } : e,
  );
}

/** Reset one agent back to its original recommendation. */
export function resetToRecommendation(
  plan: PlanEntry[],
  templateId: string,
): PlanEntry[] {
  return plan.map((e) =>
    e.templateId === templateId
      ? { ...e, areaSlug: e.recommendedSlug, manual: false }
      : e,
  );
}

/** Accept every recommendation, discarding manual edits. */
export function acceptAllRecommendations(plan: PlanEntry[]): PlanEntry[] {
  return plan.map((e) => ({
    ...e,
    areaSlug: e.recommendedSlug,
    manual: false,
  }));
}

export interface AreaGroup {
  slug: string | null;
  label: string;
  entries: PlanEntry[];
  /** True when the area is not among the instance's known/enabled areas. */
  isNew: boolean;
}

const UNASSIGNED_LABEL = "Unassigned";

/**
 * Group the plan by area for display. `areas` provides labels; `existingSlugs`
 * (optional) marks which areas already exist on the target instance so the UI
 * can flag areas that would be created on deploy.
 */
export function groupByArea(
  plan: PlanEntry[],
  areas: AreaOption[],
  existingSlugs?: Set<string>,
): AreaGroup[] {
  const labelBy = new Map(areas.map((a) => [a.slug, a.label]));
  const order = new Map(areas.map((a, i) => [a.slug, i]));
  const groups = new Map<string | null, PlanEntry[]>();
  for (const e of plan) {
    const list = groups.get(e.areaSlug) ?? [];
    list.push(e);
    groups.set(e.areaSlug, list);
  }

  const result: AreaGroup[] = [];
  for (const [slug, entries] of groups) {
    result.push({
      slug,
      label: slug ? labelBy.get(slug) ?? slug : UNASSIGNED_LABEL,
      entries,
      isNew: slug != null && existingSlugs != null && !existingSlugs.has(slug),
    });
  }

  // Stable ordering: known areas in catalogue order, then unknown, then
  // unassigned (null) last.
  result.sort((a, b) => {
    if (a.slug === null) return 1;
    if (b.slug === null) return -1;
    const ai = order.get(a.slug) ?? Number.MAX_SAFE_INTEGER;
    const bi = order.get(b.slug) ?? Number.MAX_SAFE_INTEGER;
    return ai - bi;
  });
  return result;
}

/** Deploy-time validation: which agents still lack an area. */
export function unassignedCount(plan: PlanEntry[]): number {
  return plan.filter((e) => e.areaSlug === null).length;
}
