import { defineConfig } from "vitest/config";

// Unit tests only. Playwright specs live in e2e/*.spec.ts and are run by
// `npm run test:e2e`; keep vitest away from them so the two runners don't
// collide over test.describe().
export default defineConfig({
  test: {
    include: ["src/**/*.test.ts"],
    environment: "node",
  },
});
