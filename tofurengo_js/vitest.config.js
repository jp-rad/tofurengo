import { defineConfig } from "vitest/config";
import { execSync } from "child_process";

export default defineConfig({
  plugins: [
    {
      name: "pretest-build",
      // Execute build before running tests to ensure fresh dist outputs
      buildStart() {
        console.log("\n[pretest] Building dist via npm run build...");
        execSync("npm run build", { stdio: "inherit" });
      },
    },
  ],
  test: {
    environment: "jsdom",
  },
});
