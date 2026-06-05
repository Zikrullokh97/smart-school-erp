# API Documentation

API specifications will be generated from FastAPI OpenAPI schemas and documented here as backend modules are implemented.

## Standards

- All APIs are versioned under `/api/v1`.
- Tenant-owned APIs require tenant context.
- Mutating offline-capable APIs support idempotency keys.
- Errors use a consistent structured response shape.
- Authentication, authorization, validation, and audit behavior are documented with each module.
- Student record APIs are documented in `docs/api/students.md`.
- Teacher record APIs are documented in `docs/api/teachers.md`.
- Parent record APIs are documented in `docs/api/parents.md`.
- Attendance APIs are documented in `docs/api/attendance.md`.
- Gamification APIs are documented in `docs/api/gamification.md`.
- AI review APIs are documented in `docs/api/ai_reviews.md`.
- Offline sync APIs are documented in `docs/api/sync.md`.
