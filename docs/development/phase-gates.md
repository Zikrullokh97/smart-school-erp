# Phase Gates

## Required Phase Completion Steps

Each phase must complete the following steps:

1. Implement the scoped feature or foundation.
2. Add or update automated tests.
3. Run the relevant test suite.
4. Fix all failures introduced by the phase.
5. Update documentation and roadmap status.
6. Write a progress report in `docs/progress`.
7. Commit the completed phase.

## Phase 1 Gate

Phase 1 is complete when:

- Monorepo directories exist.
- Root README explains product scope, layout, validation, and principles.
- `AGENTS.md` defines autonomous engineering instructions.
- `ROADMAP.md` tracks all required phases.
- Architecture docs cover system overview, security, offline sync, observability, and the monorepo ADR.
- The repository validation script passes.

## Future Gates

Future phases must add domain-specific tests. Backend phases require Pytest coverage. Web phases require TypeScript checks and component or E2E coverage. Mobile phases require Flutter tests. Infrastructure phases require build, deployment, and manifest validation.
