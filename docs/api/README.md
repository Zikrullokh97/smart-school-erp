# API Documentation

## Phase 10: Backend Integration

As of Phase 10, all core backend APIs are implemented and validated as a cohesive system:

- **Authentication** (`docs/api/authentication.md`): JWT login, token refresh, logout, tenant registration
- **Users** (`docs/api/authentication.md`): User management under tenant scope
- **Schools** (`docs/api/students.md`): School CRUD and hierarchy
- **Students** (`docs/api/students.md`): Student records, enrollment, profiles
- **Teachers** (`docs/api/teachers.md`): Teacher records, employment, profiles
- **Parents** (`docs/api/parents.md`): Parent profiles, UI preferences, child relationships
- **Attendance** (`docs/api/attendance.md`): Session and event capture with offline sync support
- **Gamification** (`docs/api/gamification.md`): XP awards, badges, challenges, leaderboards
- **AI Review** (`docs/api/ai_reviews.md`): Report queue, human-in-the-loop review actions
- **Offline Sync** (`docs/api/sync.md`): Device registration, operation submission, conflict resolution

## API Standards

- All APIs are versioned under `/api/v1`.
- Tenant-owned APIs use implicit tenant context from JWT token (no `tenant_id` in request body).
- Mutating APIs support optional idempotency keys for offline-capable clients.
- Errors use a consistent structured response shape.
- Authentication, authorization, validation, and audit behavior are documented with each module.
- All endpoints require `Authorization: Bearer <access_token>` header unless explicitly noted.
- All endpoints require `X-Tenant-Slug` header for tenant scoping (implicit in dependency injection).
- RBAC permissions enforced at route level via `require_permission` dependency.

## OpenAPI Documentation

Live OpenAPI schema available at `/api/v1/openapi.json` (requires authentication).

JSON Schema definitions for all request/response models auto-generated from Pydantic v2 models.
