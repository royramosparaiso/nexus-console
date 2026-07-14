import { describe, expect, it } from "vitest";

import {
  INTEGRATION_LABEL,
  STATUS_ORDER,
  statusMeta,
  totalEntries,
  type EcosystemStatus,
  type EcosystemView,
} from "./ecosystem";

const ALL_STATUSES: EcosystemStatus[] = [
  "available",
  "configurable",
  "experimental",
  "planned",
];

describe("statusMeta", () => {
  it("returns distinct labels + classes for every status", () => {
    const labels = ALL_STATUSES.map((s) => statusMeta(s).label);
    expect(new Set(labels).size).toBe(ALL_STATUSES.length);
    for (const s of ALL_STATUSES) {
      expect(statusMeta(s).className).toMatch(/text-/);
      expect(statusMeta(s).hint.length).toBeGreaterThan(10);
    }
  });

  it("falls back to planned for an unknown status", () => {
    expect(statusMeta("bogus" as EcosystemStatus).label).toBe(
      statusMeta("planned").label,
    );
  });
});

describe("STATUS_ORDER", () => {
  it("lists most-done first and covers all statuses", () => {
    expect(STATUS_ORDER[0]).toBe("available");
    expect(STATUS_ORDER[STATUS_ORDER.length - 1]).toBe("planned");
    expect(new Set(STATUS_ORDER)).toEqual(new Set(ALL_STATUSES));
  });
});

describe("INTEGRATION_LABEL", () => {
  it("labels all three integration kinds", () => {
    expect(INTEGRATION_LABEL.native).toBe("Native");
    expect(INTEGRATION_LABEL.external).toBe("External");
    expect(INTEGRATION_LABEL.catalog).toBe("Catalogue");
  });
});

describe("totalEntries", () => {
  it("sums entries across groups", () => {
    const view: EcosystemView = {
      version: "1.0.0",
      counts: {},
      groups: [
        {
          category: "voice",
          label: "Voice",
          entries: [
            {
              id: "voicebox",
              name: "Voicebox",
              category: "voice",
              status: "configurable",
              integration: "external",
              summary: "",
              provider: null,
              requires: [],
              docs_url: null,
              tags: [],
              template_id: null,
            },
          ],
        },
        { category: "llm", label: "LLMs", entries: [] },
      ],
    };
    expect(totalEntries(view)).toBe(1);
  });
});
