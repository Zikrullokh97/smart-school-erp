# Observability Architecture

## Signals

- Logs: structured JSON logs with request ID, tenant ID, actor ID, route, status, latency, and error classification.
- Metrics: RED metrics for APIs, worker throughput, outbox lag, sync conflicts, notification delivery, AI job latency, database pool health, and cache health.
- Traces: OpenTelemetry traces across API requests, database operations, Redis calls, worker jobs, and AI calls.

## Health Checks

- Liveness verifies process responsiveness.
- Readiness verifies database connectivity, Redis connectivity, migration state, and required configuration.
- Worker readiness verifies outbox access and queue dependencies.

## Audit Logs

Audit logs are domain records, not only application logs. They capture actor, tenant, action, target, before-and-after summaries where safe, request metadata, and correlation ID.

## Alerting Direction

Production alerts will focus on user-impacting symptoms and release safety:

- API error rate and latency.
- Authentication anomaly rate.
- Database connectivity and pool exhaustion.
- Outbox processing lag.
- Sync conflict spikes.
- Notification delivery failure spikes.
- AI job failure or cost anomalies.
