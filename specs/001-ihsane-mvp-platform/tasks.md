# Tasks: Ihsane MVP Platform

**Input**: Design documents from `/specs/001-ihsane-mvp-platform/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included per the project guidelines (80% minimum coverage, PyTest for backend, Vitest for frontend).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize FastAPI backend with Pydantic v2 and PostgreSQL dependencies in `backend/`
- [x] T002 Initialize Vue 3 Single Page Application with Vite, Pinia, and Tailwind in `frontend/`
- [x] T003 Setup Docker Compose for PostgreSQL 16+ and Valkey 8.x in `docker-compose.yml`
- [x] T004 [P] Configure Ruff and Prettier for the repository in `.ruff.toml` and `.prettierrc`
- [x] T005 [P] Implement `vue-i18n` plugin scaffolding for RTL Arabic and LTR French in `frontend/src/locales/`
- [x] T006 [P] Enable Dexie.js and Workbox PWA plugin in `frontend/vite.config.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Initialize Alembic and define database engine/session maker in `backend/app/db/session.py`
- [x] T008 Create `User` model, role enumerations, and Alembic migration in `backend/app/models/user.py`
- [x] T009 Implement JWT and PIN-based authentication middleware in `backend/app/core/security.py`
- [x] T010 Implement `/api/v1/auth/login/*` endpoints in `backend/app/api/endpoints/auth.py`
- [x] T011 [P] Create Axios/Fetch interceptors for JWT token injection in `frontend/src/services/api.ts`
- [x] T012 [P] Create Global Auth Store via Pinia (RBAC handling) in `frontend/src/stores/auth.ts`
- [x] T013 Setup Vue Router scaffolding and Navigation Guards based on Auth Roles in `frontend/src/router/index.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Expert Creates Content & Question Banks (Priority: P1) 🎯 MVP

**Goal**: A pedagogical expert logs into the back-office, creates a curriculum-aligned module for Mathematics, adds questions tagged with metadata, and previews them.

**Independent Test**: Can be fully tested by creating a module, adding 10+ tagged questions, previewing in student mode, and verifying the content appears in the DB with correct metadata.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Integration tests for content API endpoints in `backend/tests/api/test_content.py`
- [X] T015 [P] [US1] Component test for Expert Module Editor in `frontend/tests/components/ModuleEditor.spec.ts`

### Implementation for User Story 1

- [X] T016 [P] [US1] Create `Module`, `Question` and `KnowledgeAtom` SQLAlchemy models in `backend/app/models/content.py`
- [X] T017 [US1] Implement CRUD Services for `Module` and `Question` in `backend/app/services/content_service.py`
- [X] T018 [US1] Implement `/api/v1/content/modules` and `/questions` API routes in `backend/app/api/endpoints/content.py`
- [X] T019 [P] [US1] Create Expert Module List view in `frontend/src/views/expert/ModuleList.vue`
- [X] T020 [P] [US1] Create Question Bank Editor component in `frontend/src/components/expert/QuestionEditor.vue`
- [X] T021 [US1] Implement CSV/JSON Bulk Import logic for Questions in `frontend/src/services/importService.ts`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Student Takes Adaptive Diagnostic (Priority: P1)

**Goal**: A student takes a ~10-minute adaptive test. The system dynamically selects questions, classifies errors, places the student into a remediation group (A/B/C), and generates a competency profile.

**Independent Test**: Test by letting a student mock-account complete a diagnostic session and confirming correct group placement and error classification based on their sequence of answers.

### Tests for User Story 2 ⚠️

- [X] T022 [P] [US2] Unit test diagnostic next-question selection logic in `backend/tests/services/test_diagnostic_engine.py`
- [X] T023 [P] [US2] Component test for Student Diagnostic View in `frontend/tests/views/DiagnosticSession.spec.ts`

### Implementation for User Story 2

- [X] T024 [P] [US2] Create models `DiagnosticSession`, `DiagnosticAnswer`, and `CompetencyProfile` in `backend/app/models/diagnostic.py`
- [X] T025 [US2] Implement BKT logic and Question Selection Algorithm in `backend/app/services/diagnostic_engine.py`
- [X] T026 [US2] Implement `/api/v1/diagnostic/start` and `/answer` and `/results` endpoints in `backend/app/api/endpoints/diagnostic.py`
- [X] T027 [P] [US2] Create Student Dashboard View (Tablet-Optimized) in `frontend/src/views/student/Dashboard.vue`
- [X] T028 [US2] Implement Diagnostic Runner Interface (fetching questions lazily) in `frontend/src/components/student/DiagnosticRunner.vue`
- [X] T029 [US2] Sync offline questions into Dexie.js for uninterrupted tests in `frontend/src/stores/offlineModule.ts`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Student Follows Remediation Pathway (Priority: P1)

**Goal**: A student assigned to a specific weakness receives targeted micro-learning atoms, adapting to their speed/accuracy, concluding with a Passport validation assessment.

**Independent Test**: Verify that a student with a partial mastery level correctly receives micro-learning atoms mapped to their gaps, and that the Passport assessment blocks or advances them correctly.

### Tests for User Story 3 ⚠️

- [X] T030 [P] [US3] Unit test dynamic difficulty algorithm in `backend/tests/services/test_remediation_engine.py`
- [X] T031 [P] [US3] Integration test for Passport evaluation in `backend/tests/api/test_passport.py`

### Implementation for User Story 3

- [X] T032 [P] [US3] Create `RemediationPath` model in `backend/app/models/remediation.py`
- [X] T033 [US3] Implement dynamic atom pathway generation Service in `backend/app/services/remediation_engine.py`
- [X] T034 [US3] Implement `/api/v1/remediation/pathway` and `/passport/evaluate` endpoints in `backend/app/api/endpoints/remediation.py`
- [X] T035 [P] [US3] Create Micro-Learning UI components (Audio-Visual, MindMap variants) in `frontend/src/components/student/KnowledgeAtom.vue`
- [X] T036 [US3] Implement Passport Validation flow UI in `frontend/src/components/student/PassportAssessment.vue`

**Checkpoint**: All three P1 user stories should now be functional. The core pedagogical engine is complete.

---

## Phase 6: User Story 4 - Parent Monitors Child Progress (Priority: P2)

**Goal**: Parent views a mobile-first dashboard featuring qualitative messages, a radar chart, actionable recommendations, and a bento grid of recent activities.

**Independent Test**: Log in as a parent, verify real diagnostic data (from US2/US3) renders correctly as soft feedback (messages, radar charts) rather than harsh scores.

### Tests for User Story 4 ⚠️

- [X] T037 [P] [US4] Endpoint test for Parent Dashboard aggregator in `backend/tests/api/test_dashboard_parent.py`
- [X] T038 [P] [US4] Component test for mobile-first rendering of Radar Chart in `frontend/tests/components/RadarChart.spec.ts`

### Implementation for User Story 4

- [X] T039 [US4] Implement `/api/v1/dashboard/parent/overview` aggregation logic pulling BKT states in `backend/app/api/endpoints/dashboard.py`
- [X] T040 [P] [US4] Create Parent Dashboard mobile layout in `frontend/src/views/parent/Dashboard.vue`
- [X] T041 [US4] Implement Radar Chart component using Chart.js or SVG in `frontend/src/components/parent/SubjectRadarChart.vue`
- [X] T042 [US4] Design and integrate 'Smart Measures & Recommendations' cards in `frontend/src/components/parent/InsightCard.vue`

---

## Phase 7: User Story 5 - System Triggers Pedagogical Alerts (Priority: P2)

**Goal**: Automated generation of INFO/WARNING/CRITICAL pedagogical alerts sent to parents and experts based on session failure/abandonment triggers.

**Independent Test**: Simulate 3 consecutive exercise failures and verify the "WARNING" alert is available via the dashboard alert endpoints.

### Tests for User Story 5 ⚠️

- [X] T043 [P] [US5] Unit test alert generation logic in `backend/tests/services/test_alert_manager.py`

### Implementation for User Story 5

- [X] T044 [P] [US5] Create `PedagogicalAlert` model in `backend/app/models/alert.py`
- [X] T045 [US5] Create Background Celery Task / Service to detect warning states post-session in `backend/app/services/alert_manager.py`
- [X] T046 [US5] Implement `/api/v1/dashboard/parent/alerts` endpoint in `backend/app/api/endpoints/dashboard.py`
- [X] T047 [P] [US5] Build the Alert Notification UI widget in `frontend/src/components/common/PedagogicalAlertBox.vue`

---

## Phase 8: User Story 6 - Expert Analyzes Student Performance (Priority: P2)

**Goal**: Expert views a competency heatmap, triggers auto-grouping for remediation, and exports reports.

**Independent Test**: Fetch the heatmap data and verify that auto-grouping correctly clusters students sharing the same unmastered competency.

### Implementation for User Story 6

- [x] T048 [P] [US6] Implement `/api/v1/analytics/heatmap` and grouping logic in `backend/app/api/endpoints/analytics.py`
- [x] T049 [US6] Setup PDF/CSV Export helper service using ReportLab or CSV package in `backend/app/services/report_exporter.py`
- [x] T050 [P] [US6] Create Heatmap Component using CSS Grids or Canvas in `frontend/src/components/expert/CompetencyHeatmap.vue`
- [x] T051 [US6] Build Expert Analytics Dashboard View in `frontend/src/views/expert/Analytics.vue`

---

## Phase 9: User Story 7 - Bilingual Interface Switching (Priority: P3)

**Goal**: Seamless toggle between Arabic (RTL) and French (LTR) adapting typography, logic, and alignment dynamically.

**Independent Test**: Switch language state in-app and confirm CSS variables, text, and `dir="rtl"` update correctly without breaking the layout.

### Implementation for User Story 7

- [x] T052 [P] [US7] Migrate all hardcoded strings to `frontend/src/locales/ar.json` and `fr.json`
- [x] T053 [US7] Build Language Switcher component updating `vue-i18n` and `<html dir="...">` in `frontend/src/components/common/LanguageToggle.vue`
- [x] T054 [P] [US7] Audit and update Tailwind properties to use Logical Properties (e.g., `ml-4` -> `ms-4`) throughout the `frontend/`

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T055 [P] Setup Service Worker auto-reloads and PWA Manifest configurations in `frontend/vite.config.ts`
- [x] T056 Ensure fallback fonts (Cairo/Tajawal for Arabic, Plus Jakarta Sans for Latin) are mapped correctly in global CSS.
- [x] T057 Run end-to-end security check (JWT expiration, CORS constraints, CSP headers).
- [x] T058 Update the root README and Quickstart documentation.
- [x] T059 Run full system verification.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Stories 1, 2, and 4 can proceed concurrently.
  - User Story 3 (Remediation) depends directly on diagnostic schemas from User Story 2.
  - User Story 5 (Alerts) and 6 (Analytics) depend heavily on diagnostic and remediation data from US1, US2, and US3.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories (e.g., US1 Backend logic vs US4 Parent Frontend rendering) can be worked on in parallel by different team members spanning across FastAPI and Vue.

---

## Implementation Strategy

### MVP First (User Story 1, 2, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Content Creation)
4. Complete Phase 4: User Story 2 (Diagnostic Engine)
5. Complete Phase 5: User Story 3 (Remediation Gateway)
6. **STOP and VALIDATE**: Pilot the core mechanism. Can a created question accurately diagnose a simulated student profile and provide the correct micro-learning atom?

### Incremental Delivery (Dashboards & Insights)

1. Add Phase 6: User Story 4 (Parent UI linking to real student outcomes)
2. Add Phase 7: User Story 5 (Alert triggers checking session events quietly)
3. Add Phase 8: User Story 6 (Expose the aggregate data via Expert Analytics API)
4. Add Phase 9: Language Polishing
5. **Deploy & Demo**: Final bilingual pilot platform presentation.
