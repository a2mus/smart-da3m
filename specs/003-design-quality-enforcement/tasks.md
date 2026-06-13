---
description: "Task list template for feature implementation"
---

# Tasks: Design Quality Enforcement

**Input**: Design documents from `/specs/003-design-quality-enforcement/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Tests are excluded as this is an enforcement and remediation feature; the verifications are lint tests and audits.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize husky pre-commit hooks in `frontend/` (`npx husky init`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Fix semantic token definitions to remove `#ffffff` violations and add `ink-*` aliases in `frontend/tailwind.config.js`
- [x] T003 Fix shadow definitions to remove pure black `rgba(0,0,0,0.05)` in `frontend/tailwind.config.js`
- [x] T004 Install linting dependencies (`stylelint`, `stylelint-config-standard`, `stylelint-plugin-logical-css`, `lint-staged`) in `frontend/package.json`
- [x] T005 Create base Stylelint configuration with color/logical rules in `frontend/.stylelintrc.json`
- [x] T006 Update ESLint configuration to flag banned/physical Tailwind classes in `frontend/eslint.config.js` (or applicable eslint configs in `frontend/node_modules/**` -> standard root config)
- [x] T007 Configure lint-staged targeting Vue/CSS/TS in `frontend/.lintstagedrc.json`
- [x] T008 Update husky pre-commit hook to execute lint-staged in `frontend/.husky/pre-commit`
- [x] T009 Add npm lint and audit scripts (`lint:design`, `lint:design:fix`, `audit:a11y`, `audit:full`) in `frontend/package.json`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Designer/Developer Encounters Color Violation Feedback (Priority: P1) 🎯 MVP

**Goal**: Prevent pure whites/blacks and enforce semantic tokens through rapid feedback and retroactive visual remediation.

**Independent Test**: Introduce `#FFFFFF` in a component, verify `npm run lint:design` catches it, then replace it with `bg-surface` and verify it passes.

### Implementation for User Story 1

- [x] T010 [P] [US1] Remediate ~22 color violations in `frontend/src/views/student/Dashboard.vue`
- [x] T011 [P] [US1] Remediate ~15 color violations in `frontend/src/views/Home.vue`
- [x] T012 [P] [US1] Remediate ~12 color violations in `frontend/src/views/StudentJourney.vue`
- [x] T013 [P] [US1] Remediate ~12 color violations in `frontend/src/views/expert/Analytics.vue`
- [x] T014 [P] [US1] Remediate ~10 color violations in `frontend/src/views/Login.vue`
- [x] T015 [P] [US1] Remediate ~8 color violations in `frontend/src/views/LandingPage.vue`
- [x] T016 [P] [US1] Remediate ~8 color violations in `frontend/src/views/AnalyticsView.vue`
- [x] T017 [P] [US1] Remediate ~6 color violations in `frontend/src/views/ParentDashboard.vue`
- [x] T018 [P] [US1] Remediate ~6 color violations in `frontend/src/views/parent/Dashboard.vue`
- [x] T019 [P] [US1] Remediate color violations in minor components (`HeroSection.vue`, `CompetencyHeatmap.vue`) and verify 0 remaining issues

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (`npm run lint:design` reports no color errors).

---

## Phase 4: User Story 2 - Developer Builds an RTL-Optimized Screen (Priority: P1)

**Goal**: Ensure horizontal layout integrity in both Arabic (RTL) and French (LTR) by enforcing logical CSS properties and classes.

**Independent Test**: Use a physical class like `pl-4` in a component, verify linting fails. Toggle `dir="rtl"` in browser and see layout mirrors correctly.

### Implementation for User Story 2

- [x] T020 [P] [US2] Add safe-area exemption comments to physical padding in `frontend/src/assets/main.css`
- [x] T021 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/expert/Analytics.vue`
- [x] T022 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/AnalyticsView.vue`
- [x] T023 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/student/Dashboard.vue`
- [x] T024 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/StudentJourney.vue`
- [x] T025 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/ParentDashboard.vue`
- [x] T026 [P] [US2] Migrate physical CSS properties to logical in `frontend/src/views/parent/Dashboard.vue`
- [x] T027 [P] [US2] Migrate physical CSS properties to logical in remaining views (`Home.vue`, `LandingPage.vue`, `Login.vue`)
- [x] T028 [P] [US2] Migrate physical CSS properties to logical in components (`IhsaneButton.vue`, `CompetencyHeatmap.vue`) and verify 0 left

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. (`npm run lint:design` passes fully).

---

## Phase 5: User Story 3 - Quality Auditor Runs WCAG AA Contrast Audit (Priority: P1)

**Goal**: Automatically audit implementation for WCAG AA compliance (4.5:1 / 3:1 contrast), semantic structures, and touch target minimums.

**Independent Test**: Run `npm run audit:a11y` and verify the output script identifies accessible/inaccessible elements gracefully.

### Implementation for User Story 3

- [x] T029 [US3] Install axe-core playwright package (`@axe-core/playwright`) in `frontend/package.json`
- [x] T030 [US3] Create a11y audit script running axe-core against local dev server in `frontend/src/scripts/audit-a11y.ts`
- [x] T031 [P] [US3] Fix semantic HTML issues (landmarks, single H1) in Expert dashboard views
- [x] T032 [P] [US3] Fix semantic HTML issues in Student journey/dashboard views
- [x] T033 [P] [US3] Fix semantic HTML issues in Parent dashboard views
- [x] T034 [P] [US3] Fix semantic HTML issues in Public/Landing views
- [x] T035 [US3] Remediate baseline contrast ratio and missing label critical findings based on audit report generated by scripts

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: User Story 4 - Developer References Approved Semantic Color Scale (Priority: P2)

**Goal**: Developers have a documented source of truth mapping design intent to specific semantic tokens.

**Independent Test**: Review developer documentation against actual Tailwind config tokens.

### Implementation for User Story 4

- [x] T036 [US4] Document semantic color scale and exemption comments mapping in `frontend/README.md` and/or quickstart docs.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T037 Add `lint:design` and `audit:a11y` steps to CI pipeline in `.github/workflows/deploy.yml`
- [x] T038 Validate full UI integrity by running `npm run build` & `npm run test`
- [x] T039 Execute visual LTR/RTL cross-check manually and document passing state

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1, US2, US3, US4 can all proceed in parallel

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- All retroactive cleanup (T010 - T019) and (T020 - T028) can run independently file by file.
- Semantic HTML cleanup (T031 - T034) can run independently across different views.

---

## Parallel Example: User Story 1

```bash
# Launch validation sweeps grouped by user area
Task: "Remediate color violations in student views (Dashboard, Journey)"
Task: "Remediate color violations in parent views"
Task: "Remediate color violations in expert views" 
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Color violations fix)
4. **STOP and VALIDATE**: Confirm all pure-whites and pure-blacks are removed locally via tools.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (Lint config enforced locally)
2. Add User Story 1 (fix broken color screens)
3. Add User Story 2 (fix broken LTR classes for RTL compliance)
4. Add User Story 3 (axe-core full DOM assessment)
5. Add User Story 4 (Reference documentation)
6. Complete CI pipeline deployment in Phase 7.
