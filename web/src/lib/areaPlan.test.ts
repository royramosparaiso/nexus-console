import { describe, expect, it } from "vitest";

import {
  acceptAllRecommendations,
  groupByArea,
  reconcilePlan,
  resetToRecommendation,
  setAreaManually,
  unassignedCount,
  type AreaOption,
  type AreaRecommendation,
} from "./areaPlan";

const AREAS: AreaOption[] = [
  { slug: "finance_personal", label: "Personal finance", tier: "core" },
  { slug: "comms", label: "Communications", tier: "core" },
  { slug: "sales", label: "Sales & pipeline", tier: "vertical" },
  { slug: "legal", label: "Legal & compliance", tier: "vertical" },
  { slug: "operations", label: "Operations", tier: "vertical" },
];

function rec(
  id: string,
  slug: string | null,
  source: AreaRecommendation["source"] = "domain_match",
  candidates: string[] = [],
): AreaRecommendation {
  return {
    template_id: id,
    artifact_type: "agent",
    area_slug: slug,
    area_label: slug,
    source,
    rationale: `${id} → ${slug}`,
    candidates,
  };
}

describe("reconcilePlan", () => {
  it("auto-fills newly selected agents from recommendations", () => {
    const plan = reconcilePlan(
      [],
      [rec("a", "sales"), rec("b", "legal")],
      ["a", "b"],
    );
    expect(plan.map((e) => [e.templateId, e.areaSlug])).toEqual([
      ["a", "sales"],
      ["b", "legal"],
    ]);
    expect(plan.every((e) => !e.manual)).toBe(true);
  });

  it("preserves a manual override when selection changes", () => {
    let plan = reconcilePlan([], [rec("a", "sales")], ["a"]);
    plan = setAreaManually(plan, "a", "operations");
    // A new agent "b" is added to the selection; recs re-fetched.
    plan = reconcilePlan(plan, [rec("a", "sales"), rec("b", "legal")], ["a", "b"]);
    const a = plan.find((e) => e.templateId === "a")!;
    expect(a.areaSlug).toBe("operations"); // not overwritten by recommendation
    expect(a.manual).toBe(true);
    expect(a.recommendedSlug).toBe("sales"); // advisory metadata refreshed
    const b = plan.find((e) => e.templateId === "b")!;
    expect(b.areaSlug).toBe("legal");
  });

  it("drops entries for deselected agents (no stale recommendations)", () => {
    let plan = reconcilePlan(
      [],
      [rec("a", "sales"), rec("b", "legal")],
      ["a", "b"],
    );
    plan = reconcilePlan(plan, [rec("a", "sales")], ["a"]);
    expect(plan.map((e) => e.templateId)).toEqual(["a"]);
  });

  it("keeps a manual unassigned (null) choice", () => {
    let plan = reconcilePlan([], [rec("a", "sales")], ["a"]);
    plan = setAreaManually(plan, "a", null);
    plan = reconcilePlan(plan, [rec("a", "sales")], ["a"]);
    expect(plan[0].areaSlug).toBeNull();
    expect(plan[0].manual).toBe(true);
  });

  it("falls back to unassigned when no recommendation exists", () => {
    const plan = reconcilePlan([], [], ["ghost"]);
    expect(plan[0].areaSlug).toBeNull();
    expect(plan[0].source).toBe("fallback");
  });

  it("preserves selection order", () => {
    const plan = reconcilePlan(
      [],
      [rec("a", "sales"), rec("b", "legal"), rec("c", "comms")],
      ["c", "a", "b"],
    );
    expect(plan.map((e) => e.templateId)).toEqual(["c", "a", "b"]);
  });
});

describe("resetToRecommendation / acceptAll", () => {
  it("resets a single agent to its suggestion", () => {
    let plan = reconcilePlan([], [rec("a", "sales")], ["a"]);
    plan = setAreaManually(plan, "a", "operations");
    plan = resetToRecommendation(plan, "a");
    expect(plan[0].areaSlug).toBe("sales");
    expect(plan[0].manual).toBe(false);
  });

  it("accept-all discards manual edits", () => {
    let plan = reconcilePlan([], [rec("a", "sales"), rec("b", "legal")], ["a", "b"]);
    plan = setAreaManually(plan, "a", "operations");
    plan = acceptAllRecommendations(plan);
    expect(plan.map((e) => e.areaSlug)).toEqual(["sales", "legal"]);
    expect(plan.every((e) => !e.manual)).toBe(true);
  });
});

describe("groupByArea", () => {
  it("groups by area in catalogue order with unassigned last", () => {
    const plan = reconcilePlan(
      [],
      [rec("a", "sales"), rec("b", "finance_personal"), rec("c", null, "fallback")],
      ["a", "b", "c"],
    );
    const groups = groupByArea(plan, AREAS);
    expect(groups.map((g) => g.slug)).toEqual(["finance_personal", "sales", null]);
    expect(groups[groups.length - 1].label).toBe("Unassigned");
  });

  it("flags areas that do not yet exist on the instance", () => {
    const plan = reconcilePlan([], [rec("a", "legal")], ["a"]);
    const groups = groupByArea(plan, AREAS, new Set(["sales", "comms"]));
    const legal = groups.find((g) => g.slug === "legal")!;
    expect(legal.isNew).toBe(true);
  });
});

describe("unassignedCount", () => {
  it("counts agents without an area", () => {
    const plan = reconcilePlan(
      [],
      [rec("a", "sales"), rec("b", null, "fallback")],
      ["a", "b"],
    );
    expect(unassignedCount(plan)).toBe(1);
  });
});
