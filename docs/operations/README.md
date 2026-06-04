# Operations Documentation

Operations documentation covers local development, deployment, monitoring, incident response, backups, restores, and production hardening.

## Operational Standards

- Environments are configured through environment variables and secret stores.
- Database migrations are automated and reversible where safely possible.
- Health checks distinguish liveness and readiness.
- Production releases require passing tests, container builds, deployment validation, and rollback notes.
