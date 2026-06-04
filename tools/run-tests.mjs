import { spawnSync } from "node:child_process";

const steps = [
  {
    name: "documentation validation",
    command: process.execPath,
    args: ["tools/validate-phase1.mjs"]
  },
  {
    name: "backend lint",
    command: "uv",
    args: ["run", "ruff", "check"],
    cwd: "apps/backend"
  },
  {
    name: "backend tests",
    command: "uv",
    args: ["run", "pytest"],
    cwd: "apps/backend"
  }
];

for (const step of steps) {
  console.log(`Running ${step.name}...`);
  const result = spawnSync(step.command, step.args, {
    cwd: step.cwd ?? process.cwd(),
    encoding: "utf8",
    shell: false,
    stdio: "inherit"
  });

  if (result.error) {
    console.error(`Failed to start ${step.name}: ${result.error.message}`);
    process.exit(1);
  }

  if (result.status !== 0) {
    console.error(`${step.name} failed with exit code ${result.status}.`);
    process.exit(result.status ?? 1);
  }
}

console.log("All active repository tests passed.");
