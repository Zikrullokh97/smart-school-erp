# AI Review API Documentation

## Overview

Human-in-the-loop AI review APIs provide an approval queue, report detail retrieval, decision history, and explainability metadata.

All requests require the `X-Tenant-Slug` header to resolve the tenant context.

## Endpoints

### GET /api/v1/ai/reports/queue

Returns the current AI review queue.

Permissions

- `ai_reports.read`

Response

- `200 OK` with a list of `AIReportRead` objects.

### GET /api/v1/ai/reports/{report_id}

Returns a specific AI report.

Permissions

- `ai_reports.read`

Response

- `200 OK` with an `AIReportRead` object.
- `404 Not Found` when the report does not exist.

### GET /api/v1/ai/reports/{report_id}/history

Returns the review history for an AI report.

Permissions

- `ai_reports.read`

Response

- `200 OK` with a list of `AIReviewActionRead` objects.

### POST /api/v1/ai/reports/{report_id}/review

Submits a review decision for an AI report.

Permissions

- `ai_reports.manage`

Request body

- `decision`: review decision such as `approve`, `reject`, `escalate`, or `defer`.
- `comment`: optional human comment.
- `explainability`: structured metadata describing model reasoning, confidence, or audit evidence.
- `metadata`: arbitrary review metadata.

Response

- `200 OK` with the updated `AIReportRead` object.
- `400 Bad Request` when the decision is invalid or the report cannot be reviewed.
