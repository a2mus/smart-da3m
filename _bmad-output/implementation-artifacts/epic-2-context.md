# Epic 2 Context: Diagnostic Engine Reliability & Architecture Integrity

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Students receive accurate adaptive diagnostics powered by a stateless BKT engine that reads mastery from the database. The engine layer is separated from services, repositories handle all DB access, and all 11 tables have Alembic migrations. The engine survives restarts without losing state.

## Stories

- Story 2.1: Create Backend engines/ Layer — Extract Stateless Domain Logic
- Story 2.2: Create Backend repositories/ Layer — Centralize DB Access
- Story 2.3: Wire Diagnostic Endpoints & Services to Repositories & Engines
- Story 2.4: Complete Alembic Migrations for All 11 Core Database Tables

## Requirements & Constraints

- AD-1: DB source of truth, stateless engines. Engines must never hold in-memory state between calls.
- AD-7: Core domain loop stages 2-3 (diagnostic assessment & adaptive question selection).
- FR-9, FR-10, FR-11, FR-12, FR-13: Engine-backed diagnostic start/resume, BKT question selection, dynamic difficulty, error classification, and response time capture.

## Technical Decisions

- Engines (`backend/app/engines/`) contain pure domain logic functions or stateless classes.
- Repositories (`backend/app/repositories/`) handle database access with tenant isolation (`organization_id`).
- Services coordinate engines and repositories. Endpoints delegate to services.

## Cross-Story Dependencies

- Story 2.1 (Engines layer) and Story 2.2 (Repositories layer) provide foundational components for Story 2.3 (Wiring endpoints & services).
