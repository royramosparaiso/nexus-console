import { describe, expect, it } from "vitest";

import {
  buildCreatePayload,
  defaultSecretRefs,
  isValidBaseUrl,
  isValidEnvRef,
  probeStateMeta,
  validateProfileForm,
  type Adapter,
} from "./integrations";

const OPENAI: Adapter = {
  id: "llm_openai",
  name: "OpenAI",
  category: "llm",
  provider: "openai",
  capabilities: ["chat", "completion"],
  probe: "openai_compat",
  integration: "external",
  base_url_default: "https://api.openai.com/v1",
  fields: [],
  secrets: [
    { key: "api_key", label: "API key", env: "OPENAI_API_KEY", required: true },
  ],
  docs_url: null,
  template_id: "llm_provider",
  tags: [],
  notes: null,
};

describe("isValidEnvRef", () => {
  it("accepts env-var names", () => {
    expect(isValidEnvRef("OPENAI_API_KEY")).toBe(true);
  });
  it("rejects blank, spaced, or overlong values", () => {
    expect(isValidEnvRef("")).toBe(false);
    expect(isValidEnvRef("sk-this is a secret")).toBe(false);
    expect(isValidEnvRef("A".repeat(129))).toBe(false);
  });
});

describe("isValidBaseUrl", () => {
  it("treats empty as unset (valid)", () => {
    expect(isValidBaseUrl("")).toBe(true);
  });
  it("accepts http(s) with host", () => {
    expect(isValidBaseUrl("https://api.openai.com/v1")).toBe(true);
    expect(isValidBaseUrl("http://localhost:6333")).toBe(true);
  });
  it("rejects non-http and hostless URLs", () => {
    expect(isValidBaseUrl("file:///etc/passwd")).toBe(false);
    expect(isValidBaseUrl("notaurl")).toBe(false);
  });
});

describe("probeStateMeta", () => {
  it("maps known states to distinct tokens", () => {
    expect(probeStateMeta("reachable").className).toContain("success");
    expect(probeStateMeta("unreachable").className).toContain("error");
    expect(probeStateMeta("secret_missing").className).toContain("warning");
  });
  it("falls back to the raw state label", () => {
    expect(probeStateMeta("weird").label).toBe("weird");
  });
});

describe("defaultSecretRefs", () => {
  it("prefills the adapter's declared env names", () => {
    expect(defaultSecretRefs(OPENAI)).toEqual({ api_key: "OPENAI_API_KEY" });
  });
});

describe("validateProfileForm", () => {
  it("passes with a name and valid env ref", () => {
    expect(
      validateProfileForm(OPENAI, {
        name: "prod",
        base_url: "",
        secret_refs: { api_key: "OPENAI_API_KEY" },
      }),
    ).toEqual([]);
  });
  it("flags missing name, bad url, missing/valued secret", () => {
    const errs = validateProfileForm(OPENAI, {
      name: "",
      base_url: "file:///x",
      secret_refs: { api_key: "sk-real secret value" },
    });
    expect(errs.length).toBeGreaterThanOrEqual(3);
  });
  it("requires an env name for a required secret", () => {
    const errs = validateProfileForm(OPENAI, {
      name: "prod",
      base_url: "",
      secret_refs: { api_key: "" },
    });
    expect(errs.some((e) => /environment-variable name/.test(e))).toBe(true);
  });
});

describe("buildCreatePayload", () => {
  it("drops blank secret refs and config, trims, normalises empty url to null", () => {
    const payload = buildCreatePayload(OPENAI, {
      name: "  prod  ",
      base_url: "  ",
      config: { region: " us-east-1 ", empty: "" },
      secret_refs: { api_key: " OPENAI_API_KEY ", extra: "" },
      template_ids: ["llm_provider"],
      enabled: true,
    });
    expect(payload).toEqual({
      adapter_id: "llm_openai",
      name: "prod",
      base_url: null,
      config: { region: "us-east-1" },
      secret_refs: { api_key: "OPENAI_API_KEY" },
      template_ids: ["llm_provider"],
      enabled: true,
    });
  });
});
