---
description: "Task list for Stitch Mockup Adaptation"
---

# Tasks: Stitch Mockup Adaptation

**Input**: Design documents from `/specs/002-stitch-mockup-adaptation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story (Functional Requirements) to enable independent implementation and testing of each screen.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and asset preparation

- [x] T001 Extract design assets (images/icons) from the Stitch mockups to `frontend/public/assets/stitch/`
- [x] T002 Verify Tailwind configuration has necessary token support for the new components (checked ink, warm) in `frontend/tailwind.config.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY UI implementation can begin.

**⚠️ CRITICAL**: No UI work can begin until this phase is complete

- [x] T003 Create data models defined in Phase 1 (FocusSession, JourneyTask, etc.) in `frontend/src/models/stitchMockups.ts`
- [x] T004 Implement the singleton mock data provider in `frontend/src/services/mockUiState.ts` to supply deterministic UI state
- [x] T005 [P] Setup new placeholder routes for the 4 interfaces in `frontend/src/router/index.ts`

**Checkpoint**: Foundation ready - UI implementation can now begin independently per story/screen.

---

## Phase 3: US1 - Ihsane Landing Page (Priority: P1)

**Goal**: Implement the "Ihsane Landing Page" with routing components.

**Independent Test**: Navigate to the landing page route and verify mobile/desktop responsiveness per responsive strategies.

### Implementation for US1

- [x] T006 [P] [US1] Create the base `LandingPage.vue` view in `frontend/src/views/LandingPage.vue`
- [x] T007 [P] [US1] Create reusable `HeroSection.vue` component in `frontend/src/components/common/HeroSection.vue`
- [x] T008 [P] [US1] Create reusable `FeatureGrid.vue` component in `frontend/src/components/common/FeatureGrid.vue`
- [x] T009 [US1] Integrate `HeroSection` and `FeatureGrid` into `LandingPage.vue` and wire up mock navigation to dashboards.

**Checkpoint**: Landing page is fully functional and visually matches the Stitch mockups.

---

## Phase 4: US2 - Parent Dashboard & Analytics View (Priority: P2)

**Goal**: Implement the "Parent Dashboard" and "Analytics View", integrating dynamic data placeholders from `mockUiState.ts`.

**Independent Test**: Scenario 1 and 4: Open Parent Dashboard and drill down into the Analytics Focus interactions.

### Implementation for US2

- [x] T010 [P] [US2] Create the base `ParentDashboard.vue` view in `frontend/src/views/ParentDashboard.vue`
- [x] T011 [P] [US2] Create the base `AnalyticsView.vue` view in `frontend/src/views/AnalyticsView.vue`
- [x] T012 [P] [US2] Create `ParentNotificationsList.vue` in `frontend/src/components/parent/ParentNotificationsList.vue`
- [x] T013 [P] [US2] Create `StudentFocusChart.vue` component in `frontend/src/components/parent/StudentFocusChart.vue`
- [x] T014 [US2] Link `ParentDashboard.vue` and `AnalyticsView.vue` together, binding state from `mockUiState.ts`.
- [x] T015 [US2] Add hover and click states (modals/drawers) using local Vue refs in `AnalyticsView.vue`

**Checkpoint**: Both Parent Dashboard screens work independently with mock data interactions.

---

## Phase 5: US3 - Student Dashboard & Journey (Priority: P2)

**Goal**: Implement the "Student Dashboard & Journey" with interactive visual journey maps.

**Independent Test**: Scenario 2: Standard iPad viewport check ensuring task nodes are pressable and >60px.

### Implementation for US3

- [x] T016 [P] [US3] Create the base `StudentJourney.vue` view in `frontend/src/views/StudentJourney.vue`
- [x] T017 [P] [US3] Create `JourneyNode.vue` map point component in `frontend/src/components/student/JourneyNode.vue`
- [x] T018 [P] [US3] Create `JourneyPathSvg.vue` for the connecting lines in `frontend/src/components/student/JourneyPathSvg.vue`
- [x] T019 [US3] Assemble the map in `StudentJourney.vue` consuming the `LearningJourney` logic from the mock state.
- [x] T020 [US3] Ensure active task nodes animate or highlight according to `TaskState`.

**Checkpoint**: Student Journey acts accurately to tablet-first design logic.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 [P] Perform visual regression check of `ParentDashboard` against Stitch PNGs.
- [x] T022 [P] Perform visual regression check of `StudentJourney` against Stitch PNGs.
- [x] T023 Run verification steps from `quickstart.md` locally to finalize responsive thresholds natively.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all UI screens.
- **User Stories (Phase 3-5)**: Can proceed completely in parallel after Phase 2 since they are distinct router views.
- **Polish (Final Phase)**: Runs when UI work finishes.

### Parallel Opportunities

- All views (`LandingPage.vue`, `ParentDashboard.vue`, `StudentJourney.vue`) can be developed simultaneously.
- Different `<components/common/xyz.vue>` can be scaffolded concurrently.

---

## Implementation Strategy

### Incremental Delivery

1. Setup local mock assets and TS models (Foundation).
2. Deliver the Marketing Landing Page (MVP1).
3. Deliver Parent Analytics Flow (MVP2).
4. Deliver Student Journey (MVP3).
5. Cross-check UX fidelity.
