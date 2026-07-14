/**
 * End-to-end tests for the Agent Factory catalogue and the deploy-to-instance
 * flow. We stub /api/agent-templates and /api/instances so the tests are
 * self-contained and don't depend on backend state.
 */

import { expect, test, type Route } from "@playwright/test";

const CATALOG_STUB = {
  version: "0.13.0",
  total: 3,
  cards: [
    {
      id: "banking_ops_agent",
      name: "banking_ops_agent",
      artifact_type: "agent",
      lifecycle: "ops",
      category: "back-office",
      phase: null,
      step: null,
      domain: "back-office",
      rollout_stage: "4-orchestrate",
      autonomy: "human-led",
      maturity: 1,
      verticals: ["any"],
      role: "writer",
      mode: "single-shot",
      depends_on: [],
      produces: "markdown_report",
      tools: ["banking_api"],
      tags: ["banking"],
      gate: false,
      optional: false,
      path: "back-office/banking_ops_agent.md",
    },
    {
      id: "contact_enrichment_skill",
      name: "contact_enrichment_skill",
      artifact_type: "skill",
      lifecycle: "ops",
      category: "skills",
      phase: null,
      step: null,
      domain: "sales",
      rollout_stage: "2-capture",
      autonomy: "fully-autonomous",
      maturity: 3,
      verticals: ["any"],
      role: null,
      mode: null,
      depends_on: [],
      produces: null,
      tools: [],
      tags: ["enrichment"],
      gate: false,
      optional: false,
      path: "skills/contact_enrichment_skill.md",
    },
    {
      id: "crm_sync_sidecar",
      name: "crm_sync_sidecar",
      artifact_type: "sidecar",
      lifecycle: "ops",
      category: "back-office",
      phase: null,
      step: null,
      domain: "back-office",
      rollout_stage: "2-capture",
      autonomy: "fully-autonomous",
      maturity: 2,
      verticals: ["any"],
      role: "connector",
      mode: "scheduled",
      depends_on: [],
      produces: "side_effect",
      tools: ["hubspot_api"],
      tags: ["crm"],
      gate: false,
      optional: false,
      path: "back-office/crm_sync_sidecar.md",
    },
  ],
  indexes: {
    by_artifact_type: {
      agent: ["banking_ops_agent"],
      sidecar: ["crm_sync_sidecar"],
      skill: ["contact_enrichment_skill"],
    },
    by_lifecycle: {
      ops: ["banking_ops_agent", "contact_enrichment_skill", "crm_sync_sidecar"],
    },
    by_category: {},
    by_phase: {},
    by_domain: {
      "back-office": ["banking_ops_agent", "crm_sync_sidecar"],
      sales: ["contact_enrichment_skill"],
    },
    by_rollout_stage: {},
    by_autonomy: {},
    by_role: {},
    by_mode: {},
    by_verticals: {},
    by_tag: {},
  },
  enums: {
    artifact_type: ["agent", "sidecar", "skill"],
    lifecycle: ["project", "ops", "both", "none"],
    rollout_stage: ["1-foundation", "2-capture", "3-generate", "4-orchestrate"],
    autonomy: ["human-led", "human-assisted", "fully-autonomous"],
    ops_domains: [
      "sales",
      "deals",
      "marketing",
      "operations",
      "intelligence",
      "customer",
      "back-office",
    ],
    lifecycle_categories: [
      "intake",
      "market-research",
      "mvs",
      "validation",
      "scaling",
      "investor-deliverable",
      "finance",
    ],
    verticals: ["any", "real-estate", "marketing-agency", "nightclub"],
  },
};

const CARD_DETAIL_STUB = {
  card: CATALOG_STUB.cards[0],
  body: "# banking_ops_agent\n\n## Identity\n\nagent that produces reports.\n",
};

const RUNNING_INSTANCE = {
  instance_id: "00000000-0000-4000-8000-000000000001",
  name: "console-prod",
  persona_display_name: "Console",
  persona_kind: "individual",
  modality: "text",
  agent_runtime: "openai",
  auth_provider: "clerk",
  endpoint: "http://127.0.0.1:9000",
  version: "0.13.0",
  status: "running",
  created_at: "2026-07-14T00:00:00Z",
  bootstrapped_at: "2026-07-14T00:00:00Z",
};

const DEFAULT_CMD_ID = "11111111-1111-4111-8111-111111111111";

async function stubApi(
  page: import("@playwright/test").Page,
  opts: {
    instances?: unknown[];
    commandStatus?: number;
    commandBody?: unknown;
    // Sequence of statuses returned by GET /commands/{cmd_id}. The last entry
    // is returned indefinitely so the client eventually sees a terminal state.
    statusSequence?: Array<
      "queued" | "in_progress" | "applied" | "failed" | "rejected"
    >;
    cmdId?: string;
  } = {},
) {
  const cmdId = opts.cmdId ?? DEFAULT_CMD_ID;
  const sequence = opts.statusSequence ?? ["queued", "in_progress", "applied"];
  let cursor = 0;

  await page.route("**/api/agent-templates", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(CATALOG_STUB),
    });
  });
  await page.route("**/api/agent-templates/*", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(CARD_DETAIL_STUB),
    });
  });
  await page.route("**/api/instances", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(opts.instances ?? [RUNNING_INSTANCE]),
    });
  });
  await page.route("**/api/instances/*/commands/*", async (route: Route) => {
    const status = sequence[Math.min(cursor, sequence.length - 1)];
    cursor += 1;
    const url = new URL(route.request().url());
    const parts = url.pathname.split("/");
    const returnedCmd = parts[parts.length - 1];
    const instanceId = parts[parts.length - 3];
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        cmd_id: returnedCmd,
        instance_id: instanceId,
        kind: "deploy_agent",
        status,
        detail: status === "failed" ? "platform said no" : null,
        error_code: null,
        created_at: "2026-07-14T00:00:00Z",
        updated_at: "2026-07-14T00:00:01Z",
        applied_at: status === "applied" ? "2026-07-14T00:00:01Z" : null,
      }),
    });
  });
  await page.route("**/api/instances/*/command", async (route: Route) => {
    await route.fulfill({
      status: opts.commandStatus ?? 202,
      contentType: "application/json",
      body: JSON.stringify(
        opts.commandBody ?? {
          accepted: true,
          cmd_id: cmdId,
          status: "queued",
          detail: null,
        },
      ),
    });
  });
}

test("catalogue renders with cards and filter chips", async ({ page }) => {
  await stubApi(page);
  await page.goto("/#/agents");
  await expect(page.getByTestId("text-page-title")).toHaveText("Agent Factory");
  await expect(page.getByTestId("text-result-count")).toHaveText("3");
  await expect(page.getByTestId("card-banking_ops_agent")).toBeVisible();
  await expect(page.getByTestId("card-contact_enrichment_skill")).toBeVisible();
  await expect(page.getByTestId("card-crm_sync_sidecar")).toBeVisible();
});

test("artifact filter narrows results", async ({ page }) => {
  await stubApi(page);
  await page.goto("/#/agents");
  await page.getByTestId("filter-artifact-sidecar").click();
  await expect(page.getByTestId("text-result-count")).toHaveText("1");
  await expect(page.getByTestId("card-crm_sync_sidecar")).toBeVisible();
  await expect(page.getByTestId("card-banking_ops_agent")).not.toBeVisible();
});

test("deploy dispatches command then polls to applied with auto-close and toast", async ({
  page,
}) => {
  const commandRequests: string[] = [];
  await stubApi(page);
  // Wrap the POST route so we can capture the outgoing body while still
  // returning the 202 accepted envelope.
  await page.route("**/api/instances/*/command", async (route: Route) => {
    const body = route.request().postData();
    if (body) commandRequests.push(body);
    await route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({
        accepted: true,
        cmd_id: "22222222-2222-4222-8222-222222222222",
        status: "queued",
        detail: null,
      }),
    });
  });

  await page.goto("/#/agents");
  await page.getByTestId("card-banking_ops_agent").click();
  await expect(page.getByTestId("detail-panel")).toBeVisible();
  await page.getByTestId("button-deploy").click();
  await expect(page.getByTestId("dialog-deploy")).toBeVisible();

  // Instance should be preselected (only one running instance)
  await expect(
    page.getByTestId(`option-instance-${RUNNING_INSTANCE.instance_id}`),
  ).toBeVisible();

  await page.getByTestId("button-confirm-deploy").click();

  // Pipeline should render (queued → in_progress → applied)
  await expect(page.getByTestId("progress-pipeline")).toBeVisible();
  await expect(page.getByTestId("text-deploy-success")).toBeVisible({
    timeout: 10_000,
  });

  // Global toast pops from the ToastProvider portal, not from inside the modal.
  await expect(page.getByTestId("toast-success")).toBeVisible();
  await expect(page.getByTestId("toast-title")).toContainText(
    "Deployed banking_ops_agent",
  );

  // Modal auto-closes ~2s after success.
  await expect(page.getByTestId("dialog-deploy")).toBeHidden({
    timeout: 5_000,
  });

  // Toast survives modal close (proves it's a global overlay).
  await expect(page.getByTestId("toast-success")).toBeVisible();

  // Verify the request went out with kind=deploy_agent and correct template id
  expect(commandRequests).toHaveLength(1);
  const parsed = JSON.parse(commandRequests[0]);
  expect(parsed.kind).toBe("deploy_agent");
  expect(parsed.payload.template_id).toBe("banking_ops_agent");
  expect(parsed.payload.artifact_type).toBe("agent");
});

test("deploy shows failed stage and error toast when platform rejects", async ({
  page,
}) => {
  await stubApi(page, {
    statusSequence: ["queued", "in_progress", "failed"],
  });

  await page.goto("/#/agents");
  await page.getByTestId("card-banking_ops_agent").click();
  await page.getByTestId("button-deploy").click();
  await page.getByTestId("button-confirm-deploy").click();

  await expect(page.getByTestId("text-deploy-error")).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByTestId("toast-error")).toBeVisible();
  // Modal does NOT auto-close on failure — user should stay to read the error.
  await expect(page.getByTestId("dialog-deploy")).toBeVisible();
});

test("deploy button is disabled for skills", async ({ page }) => {
  await stubApi(page);
  await page.route("**/api/agent-templates/contact_enrichment_skill", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        card: CATALOG_STUB.cards[1],
        body: "# contact_enrichment_skill\n\n## Identity\n\nreusable skill.\n",
      }),
    });
  });

  await page.goto("/#/agents");
  await page.getByTestId("card-contact_enrichment_skill").click();
  await expect(page.getByTestId("detail-panel")).toBeVisible();
  await expect(page.getByTestId("button-deploy")).toBeDisabled();
});

test("deploy shows empty state when no running instances", async ({ page }) => {
  await stubApi(page, {
    instances: [{ ...RUNNING_INSTANCE, status: "provisioning" }],
  });
  await page.goto("/#/agents");
  await page.getByTestId("card-banking_ops_agent").click();
  await page.getByTestId("button-deploy").click();
  await expect(page.getByTestId("dialog-deploy")).toBeVisible();
  await expect(page.getByTestId("text-no-instances")).toBeVisible();
  await expect(page.getByTestId("button-confirm-deploy")).toBeDisabled();
});

test("deploy surfaces backend errors", async ({ page }) => {
  await stubApi(page, {
    commandStatus: 409,
    commandBody: { detail: "instance not running (status=stopped)" },
  });
  await page.goto("/#/agents");
  await page.getByTestId("card-banking_ops_agent").click();
  await page.getByTestId("button-deploy").click();
  await page.getByTestId("button-confirm-deploy").click();
  // 409 rejects at the POST stage before we ever start polling — the error
  // block inside the dialog and the global error toast both show up.
  await expect(page.getByTestId("text-deploy-error")).toBeVisible();
  await expect(page.getByTestId("toast-error")).toBeVisible();
});
