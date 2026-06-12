# Tasks: Navigation Restructure & Role-Based User Experience

**Input**: Design documents from `/specs/005-navigation-restructure/`
**Prerequisites**: plan.md, spec.md
**Organization**: Tasks grouped by phase. Full dashboard rebuilds (US3-US5) deferred to features 008/010/011.

## Phase 1: Route Cleanup (Foundation)

- [ ] T001 Remove Stitch mockup routes from router (`/parent-dashboard`, `/parent/analytics`, `/student/journey`, `/mock-auth`) and delete mockup view files in `frontend/src/router/index.ts`, `frontend/src/views/ParentDashboard.vue`, `frontend/src/views/AnalyticsView.vue`, `frontend/src/views/StudentJourney.vue`, `frontend/src/views/MockAuth.vue`
- [ ] T002 Delete `mockUiState.ts` service (superseded by spec 004 removal) in `frontend/src/services/mockUiState.ts`
- [ ] T003 Remove `useMockUiStore` import and mock auth guard from router in `frontend/src/router/index.ts`
- [ ] T004 Update LandingPage to route CTAs to `/login` instead of `/mock-auth` in `frontend/src/views/LandingPage.vue`
- [ ] T005 Delete `Home.vue` (merged into LandingPage) in `frontend/src/views/Home.vue`

## Phase 2: Auth Flow Enhancement (US2)

- [ ] T006 Create RolePicker component with 3 role cards (Parent/Expert/Student) in `frontend/src/components/common/RolePicker.vue`
- [ ] T007 Create PinInput component (4-6 digit PIN entry) in `frontend/src/components/common/PinInput.vue`
- [ ] T008 Redesign Login.vue with role picker first, then role-specific form in `frontend/src/views/Login.vue`
- [ ] T009 Update auth store for student PIN login with parent email in `frontend/src/stores/auth.ts`
- [ ] T010 Update router guards to redirect authenticated users from landing/login to their dashboard in `frontend/src/router/index.ts`

## Phase 3: Landing Page Polish (US1)

- [ ] T011 Ensure landing page has clear Sign Up / Sign In CTAs routing to `/register` and `/login` in `frontend/src/views/LandingPage.vue`
- [ ] T012 Add "How It Works" section with 3-step explainer (if not present)

## Phase 4: Verification

- [ ] T013 Remove references to deleted mockup components from router and imports
- [ ] T014 Build check — verify no broken imports
- [ ] T015 Verify route guards: unauthenticated → /login, authenticated → dashboard redirect
