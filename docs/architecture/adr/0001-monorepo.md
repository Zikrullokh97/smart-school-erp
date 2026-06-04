# ADR 0001: Use A Modular Monorepo

## Status

Accepted

## Context

Smart School Cloud ERP includes a backend API, web dashboard, Flutter mobile app, shared API contracts, generated clients, infrastructure, and documentation. These parts must evolve together because tenant isolation, permission semantics, sync contracts, and deployment configuration cross runtime boundaries.

## Decision

Use a modular monorepo with app boundaries under `apps`, reusable contract and configuration packages under `packages`, infrastructure under `infra`, and product/architecture/operations documentation under `docs`.

## Consequences

- Cross-runtime changes can be reviewed, tested, and versioned together.
- Generated API contracts can be produced from backend schemas and consumed by web and mobile clients in the same repository.
- CI can run targeted phase gates while still supporting full release validation.
- Ownership boundaries must stay explicit so the monorepo does not become a single tangled application.
