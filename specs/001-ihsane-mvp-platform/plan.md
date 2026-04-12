# Implementation Plan: Ihsane MVP Platform

**Branch**: `001-ihsane-mvp-platform` | **Date**: 2026-04-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ihsane-mvp-platform/spec.md`

## Summary

Build the Ihsane adaptive learning platform MVP, focusing on the core pedagogical engine: adaptive diagnostic tests, conditional remediation pathways using micro-learning (knowledge atoms), a parent dashboard for qualitative tracking, pedagogical alerts for interventions, an expert back-office for content creation, and advanced analytics for cohort insights. The architecture is a hybrid offline-intelligent SPA built with Vue 3 / Vite, backed by an async Python FastAPI monolith and PostgreSQL, designed specifically for the Algerian primary education system (bilingual Arabic/French).

## Technical Context

**Language/Version**: Python 3.12+ (Backend) / TypeScript + Vue 3.5+ (Frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, Alembic, Celery / Vite 6+, Pinia, Workbox, Dexie.js
**Storage**: PostgreSQL 16+ (Primary), Valkey 8.x (Cache/Sessions/Broker), Dexie.js (Offline Cache)
**Testing**: PyTest (Backend), Vitest (Frontend)
**Target Platform**: Modern web browsers (Chrome, Firefox, Edge, Safari) / Offline-capable via PWA/Service Workers
**Project Type**: Monolithic Async web API + Single Page Application
**Performance Goals**: < 200 ms API response (P95), < 500 ms algorithmic question serving, < 3s page load on 3G, < 200 KB gzipped frontend bundle
**Constraints**: Deep RTL support, mobile-first dashboards (parents), offline viability (students), minimum PII (students)
**Scale/Scope**: < 500 concurrent users for MVP pilot, limited to Mathematics for 2 grade levels initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **System Architecture**: Hybrid offline-intelligent SPA / Monolithic Async API [PASS]
- **Technology Stack**: Vue 3 / Vite + FastAPI / PostgreSQL [PASS]
- **Dependency Threshold**: Strict < 100KB gzipped limit on new frontend dependencies [PASS]
- **Testing**: 80% coverage via Vitest/Pytest [PASS]
- **Design System**: Nurturing Soft Modernism, asymmetric borders, no pure whites/blacks [PASS]
- **Accessibility**: RTL-first, 60px touch targets for students [PASS]
- **Security**: RBAC via JWT, PIN access for students tied to parents [PASS]

## Project Structure

### Documentation (this feature)

```text
specs/001-ihsane-mvp-platform/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── services/
└── tests/

frontend/
├── src/
│   ├── assets/
│   ├── components/
│   ├── composables/
│   ├── locales/
│   ├── services/
│   ├── stores/
│   └── views/
└── tests/
```

**Structure Decision**: Web application separated by `backend/` and `frontend/` folders mapped to Docker Compose. This cleanly splits the offline-capable Vue SPA from the PyTest-tested FastAPI backend monolith as mandated by the constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No violations present. Architecture maps perfectly to the defined MVP requirements.)*
