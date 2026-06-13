# Tasks: Mock Authentication Flow & UI State Architecture

**Input**: Design documents from `/specs/004-mock-auth-state/`
**Prerequisites**: plan.md, spec.md
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Phase 1: Setup

- [ ] T001 [P] Create Pinia mock UI store with all state, getters, and actions in `frontend/src/stores/mockUiStore.ts`
- [ ] T002 [P] Create MockAuth view with role-selection cards (Student/Parent/Expert) in `frontend/src/views/MockAuth.vue`

## Phase 2: Router & Navigation (Blocking)

- [ ] T003 Add `/mock-auth` route and update navigation guard for mock auth in `frontend/src/router/index.ts`
- [ ] T004 Update LandingPage CTA `startNow()` to route to `/mock-auth` in `frontend/src/views/LandingPage.vue`

## Phase 3: Dashboard Integration (US3 — Mock Data Display)

- [ ] T005 Add "Change Role" button to ParentDashboard in `frontend/src/views/ParentDashboard.vue`
- [ ] T006 Add "Change Role" button to StudentJourney in `frontend/src/views/StudentJourney.vue`
- [ ] T007 Add "Change Role" button to AnalyticsView in `frontend/src/views/AnalyticsView.vue`

## Phase 4: Verification & Polish

- [ ] T008 Verify full flow: Landing → CTA → MockAuth → role select → dashboard → Change Role → back
- [ ] T009 Verify router guard redirects unauthenticated direct access to `/mock-auth`
- [ ] T010 Verify mock store is Pinia DevTools visible with named actions
