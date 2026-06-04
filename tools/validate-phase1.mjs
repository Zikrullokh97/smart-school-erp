import { existsSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();

const requiredPaths = [
  "README.md",
  "AGENTS.md",
  "ROADMAP.md",
  "package.json",
  "pnpm-workspace.yaml",
  ".env.example",
  "apps/backend/README.md",
  "apps/web/README.md",
  "apps/mobile/README.md",
  "packages/shared-contracts/README.md",
  "packages/config/README.md",
  "infra/README.md",
  "tooling/README.md",
  "docs/product/requirements.md",
  "docs/architecture/overview.md",
  "docs/architecture/security.md",
  "docs/architecture/offline-sync.md",
  "docs/architecture/observability.md",
  "docs/architecture/adr/0001-monorepo.md",
  "docs/development/phase-gates.md",
  "docs/testing/strategy.md",
  "docs/api/README.md",
  "docs/operations/README.md",
  "docs/progress/phase-01-repository-foundation.md"
];

const requiredRoadmapPhases = Array.from({ length: 20 }, (_, index) => `| ${index + 1} |`);
const bannedPatterns = [
  /\bTODO\b/i,
  /\bFIXME\b/i,
  /\bPLACEHOLDER\b/i,
  /\bSTUB\b/i
];

function readRequiredFile(relativePath) {
  const absolutePath = join(root, relativePath);
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing required path: ${relativePath}`);
  }

  const stats = statSync(absolutePath);
  if (!stats.isFile()) {
    throw new Error(`Required path is not a file: ${relativePath}`);
  }

  const content = readFileSync(absolutePath, "utf8");
  if (content.trim().length === 0) {
    throw new Error(`Required file is empty: ${relativePath}`);
  }

  for (const pattern of bannedPatterns) {
    if (pattern.test(content)) {
      throw new Error(`Banned marker found in ${relativePath}: ${pattern}`);
    }
  }

  return content;
}

for (const relativePath of requiredPaths) {
  readRequiredFile(relativePath);
}

const roadmap = readRequiredFile("ROADMAP.md");
for (const phaseMarker of requiredRoadmapPhases) {
  if (!roadmap.includes(phaseMarker)) {
    throw new Error(`ROADMAP.md does not include phase marker: ${phaseMarker}`);
  }
}

const agents = readRequiredFile("AGENTS.md");
for (const expected of ["Definition of Done", "tenant", "tests", "documentation"]) {
  if (!agents.toLowerCase().includes(expected.toLowerCase())) {
    throw new Error(`AGENTS.md is missing expected guidance: ${expected}`);
  }
}

const overview = readRequiredFile("docs/architecture/overview.md");
for (const expected of ["FastAPI", "Next.js", "Flutter", "PostgreSQL", "Redis", "outbox"]) {
  if (!overview.includes(expected)) {
    throw new Error(`Architecture overview is missing: ${expected}`);
  }
}

console.log("Phase 1 repository validation passed.");
