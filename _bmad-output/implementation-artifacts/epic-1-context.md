# Epic 1 Context: Multi-Tenant Platform Foundation

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

The platform safely hosts multiple school organizations and independent household families on the same deployment, with complete data isolation. An independent parent can self-register, get an auto-created household org, create child accounts, and select a curriculum level. Every query is automatically tenant-filtered. The JWT carries organization context.

## Stories

- Story 1.1: Axios Snake↔Camel Transform & Frontend HTTP Boundary
- Story 1.2: Organization & OrganizationMember Models + Migrations
- Story 1.3: Add organization_id FK to All Tenant-Scoped Models
- Story 1.4: Tenant Middleware — Automatic Query Filtering
- Story 1.5: JWT Organization Claims & Auth Flow Update
- Story 1.6: Self-Registration Flow for Independent Parents
- Story 1.7: Frontend Org Switcher Component
- Story 1.8: Fix RBAC Enum Case Mismatch & Analytics Auth

## Requirements & Constraints

- Axios service layer automatically transforms snake_case API responses to camelCase and camelCase requests to snake_case.
- Vue components and stores must never handle snake_case keys directly.
- Multi-tenant data isolation per organization (SCHOOL and HOUSEHOLD).
- JWT carries organization membership pairs `(organization_id, role)`.
- Tenant middleware injects request-scoped active organization context into repository queries.
- RBAC role checks must use exact enum case values (`EXPERT`, `PARENT`, `STUDENT`).

## Technical Decisions

- AD-4: Multi-tenant (Schools + Households) architecture.
- Frontend Axios interceptors in `frontend/src/services/api.ts` handle request/response key transformations using `lodash-es` or `camelcase-keys`/`decamelize-keys` / custom utilities.
- Centralized repositories in backend enforce `organization_id` filter automatically.
