# Product Requirements

## Goal

Smart School Cloud ERP gives Kyrgyzstan schools a secure cloud platform for daily administration, attendance, communication, reporting, and planning.

## Primary Users

- Platform administrators manage tenants, subscriptions, operational health, and support.
- School administrators manage school setup, staff, students, parents, classes, schedules, and reports.
- Teachers manage class rosters, attendance, communication, and student progress workflows.
- Parents receive notifications, attendance updates, announcements, and school communication.
- Attendance operators capture classroom or gate attendance with online and offline workflows.

## Core Product Capabilities

- Multi-tenant school management.
- User management with RBAC and tenant-scoped permissions.
- Student, teacher, and parent records.
- Attendance capture, auditability, and reporting.
- Face ID infrastructure for consent-aware attendance support.
- Notification delivery through in-app and future external channels.
- AI reporting and summarization with human review paths.
- Smart scheduling for classes, rooms, teachers, and constraints.
- Offline-first mobile sync for field and classroom reliability.

## Localization And Regional Fit

- The product is designed for Kyrgyzstan school operations.
- Text and data models must support Kyrgyz, Russian, and English.
- Date, time, school year, and reporting assumptions must be configurable per tenant.

## Non-Functional Requirements

- Strong tenant isolation.
- Production-grade authentication and authorization.
- Auditable changes for sensitive records.
- Idempotent APIs for mobile and event-driven workflows.
- Observable services with logs, metrics, traces, and health checks.
- Automated tests across backend, frontend, mobile, infrastructure, and deployment gates.
