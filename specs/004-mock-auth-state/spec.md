# Feature Specification: Mock Authentication Flow & UI State Architecture

**Feature Branch**: `004-mock-auth-state`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Update the specification to clarify the mock authentication flow and the state management architecture. Specifically, define what happens when users route from the landing page to 'authentication/dashboards'—whether this should trigger a minimal mock auth view or if we should treat it as a placeholder for now. Additionally, explicitly mandate the use of a Pinia store for the mock state (e.g., useMockUiStore.ts) instead of simple local Vue refs or a generic singleton, to align with our established Vue 3 architecture.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Visitor Navigates From Landing Page to Dashboard Preview (Priority: P1)

A visitor arrives on the Ihsane landing page (`/`) and clicks "ابدأ الآن" (Start Now) or any CTA button. Instead of being silently redirected to a blank login page, they encounter a minimal mock authentication gate — a lightweight role-selection screen that lets them choose to preview the platform as a Student, Parent, or Expert. Upon selecting a role, they are instantly granted mock session state and redirected to the corresponding dashboard view with realistic placeholder data.

**Why this priority**: Without a clear authentication flow, the CTA buttons on the landing page dead-end into a non-functional login form that requires a real backend. This blocks all frontend demonstration, stakeholder review, and design iteration. A mock auth gate is the critical bridge between the marketing landing page and the dashboard experiences.

**Independent Test**: Can be fully tested by navigating to `/`, clicking the CTA, selecting a role on the mock auth screen, and verifying that the user arrives at the correct dashboard view with the mock identity persisted in the Pinia store.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they click any CTA button (header "ابدأ الآن" or footer "سجل الآن مجاناً"), **Then** they are routed to the mock authentication view at `/mock-auth`.
2. **Given** a visitor on the mock auth view, **When** they select the "Student" role, **Then** the system sets a mock session in the Pinia store with a student identity and redirects to `/student/journey`.
3. **Given** a visitor on the mock auth view, **When** they select the "Parent" role, **Then** the system sets a mock session in the Pinia store with a parent identity and redirects to `/parent-dashboard`.
4. **Given** a visitor on the mock auth view, **When** they select the "Expert" role, **Then** the system sets a mock session in the Pinia store with an expert identity and redirects to `/parent/analytics` (Expert Analytics view).
5. **Given** a visitor who has already selected a mock role, **When** they navigate back to the landing page and click a CTA again, **Then** they are taken directly to their previously selected dashboard without re-selecting a role.
6. **Given** a mock-authenticated user on any dashboard, **When** they click a "Logout" or "Change Role" action, **Then** the mock session is cleared from the Pinia store and they are redirected to `/mock-auth`.

---

### User Story 2 — Pinia Store Centralizes All Mock UI State (Priority: P1)

A developer working on any dashboard view (Parent Dashboard, Student Journey, Analytics, Landing Page) accesses mock data — the current user identity, selected role, mock student profiles, sample competency data — through a single centralized Pinia store (`useMockUiStore`). No component uses local `ref()` variables or ad-hoc singletons for shared UI state. All mock data mutations flow through store actions, ensuring a consistent, predictable, and debuggable state tree.

**Why this priority**: Without a centralized store, individual views drift into inconsistent local state patterns that make navigation, role-switching, and data sharing fragile. This is a foundational architectural constraint that all other UI features depend on.

**Independent Test**: Can be fully tested by inspecting the Pinia DevTools to confirm all mock state resides in the `mockUi` store, verifying no component-local `ref()` is used for shared data, and confirming that store actions correctly propagate state to all consuming views.

**Acceptance Scenarios**:

1. **Given** the application source code, **When** a developer searches for shared state, **Then** all mock session data (current user, role, mock students, competency profiles) is managed exclusively within `useMockUiStore`.
2. **Given** a developer creating a new view that needs mock data, **When** they import state, **Then** they use `useMockUiStore()` from `@/stores/mockUiStore.ts` — never creating local `ref()` variables for data that is shared across views.
3. **Given** the Pinia DevTools open in the browser, **When** a user navigates between dashboards, **Then** all state transitions are visible in the `mockUi` store's timeline with clear action names.
4. **Given** the mock store is initialized, **When** any view reads from it, **Then** the data is reactive and updates automatically when store state changes.
5. **Given** the existing `useAuthStore` for real authentication, **When** the mock store is active, **Then** there is no collision or interference — mock state operates independently alongside the real auth store.

---

### User Story 3 — Dashboard Views Display Realistic Mock Data (Priority: P2)

When a mock-authenticated user navigates to any dashboard view, they see realistic placeholder data — a student with an Arabic name, competency scores, recent activity history, alert notifications — pulled from the centralized Pinia store. The experience is indistinguishable from a real session for demonstration purposes.

**Why this priority**: Mock data quality directly impacts stakeholder buy-in and design validation. Without realistic data, dashboards feel hollow and design feedback is unreliable. However, this depends on the mock auth flow (P1) being functional first.

**Independent Test**: Can be fully tested by completing mock auth as each role and verifying that all dashboard widgets render with non-trivial data (names in Arabic, competency percentages, chart data points, alert messages).

**Acceptance Scenarios**:

1. **Given** a mock-authenticated parent on `/parent-dashboard`, **When** the dashboard loads, **Then** they see at least one child profile with an Arabic name, a radar chart with 3+ subject data points, and at least 2 smart messages.
2. **Given** a mock-authenticated student on `/student/journey`, **When** the view loads, **Then** they see their mock name, current competency level, and at least one available remediation pathway.
3. **Given** a mock-authenticated expert on the analytics view, **When** the view loads, **Then** they see a competency heatmap populated with at least 5 mock students and 3 competencies.
4. **Given** any mock-authenticated user, **When** they view recent activity, **Then** timestamps are relative to the current date (e.g., "today", "yesterday"), not hardcoded past dates.

---

### Edge Cases

- What happens when a visitor directly navigates to a dashboard URL (e.g., `/parent-dashboard`) without going through mock auth? → The router guard checks the mock store for an active session; if absent, the visitor is redirected to `/mock-auth`.
- What happens if the Pinia store persist plugin is not available? → Mock state is stored in-memory only; the user re-selects their role on page refresh. No `localStorage` is required for mock state.
- How does the mock auth flow coexist with the real auth flow? → Routes for mock views use `meta: { public: true }` and are guarded by the mock store, not the real `useAuthStore`. The real auth flow at `/login` remains unchanged.
- What happens when the backend becomes available and we no longer need mock auth? → The `/mock-auth` route and `useMockUiStore` can be removed without affecting any production code. All real authentication continues to use `useAuthStore`.
- What if a developer accidentally uses a local `ref()` for shared state? → The code review checklist and linting rules flag any `ref()` usage in views that should use the Pinia store instead.

## Requirements *(mandatory)*

### Functional Requirements

#### Mock Authentication Flow

- **FR-001**: System MUST provide a dedicated mock authentication route at `/mock-auth` that presents a role-selection interface with three options: Student, Parent, and Expert.
- **FR-002**: The mock authentication view MUST visually align with the Ihsane "Nurturing Soft Modernism" design constitution — warm tones, rounded cards, RTL-first layout, and bilingual labels.
- **FR-003**: System MUST redirect all landing page CTA buttons ("ابدأ الآن", "سجل الآن مجاناً") to `/mock-auth` instead of the real `/login` route.
- **FR-004**: Upon role selection on the mock auth view, the system MUST set a mock session in the `useMockUiStore` Pinia store and redirect to the appropriate dashboard route:
  - Student → `/student/journey`
  - Parent → `/parent-dashboard`
  - Expert → `/parent/analytics`
- **FR-005**: System MUST provide a "Change Role" action accessible from any mock-authenticated dashboard that clears the mock session and returns to `/mock-auth`.
- **FR-006**: System MUST implement a router navigation guard that redirects unauthenticated visitors to `/mock-auth` when they attempt to access any dashboard route directly.

#### Pinia Store Architecture

- **FR-010**: All shared mock UI state MUST be managed through a single Pinia store defined in `src/stores/mockUiStore.ts` using the Composition API style (consistent with the existing `useAuthStore`).
- **FR-011**: The mock UI store MUST expose the following state:
  - `currentMockRole`: The currently selected mock role (`'STUDENT' | 'PARENT' | 'EXPERT' | null`)
  - `isMockAuthenticated`: Boolean computed getter derived from `currentMockRole !== null`
  - `mockUser`: A mock user object matching the `User` interface shape from `useAuthStore`
  - `mockStudents`: Array of mock student profiles with Arabic names, grade levels, and competency data
  - `mockAlerts`: Array of mock pedagogical alerts with severity levels
  - `mockCompetencyData`: Structured competency profiles for radar charts and heatmaps
- **FR-012**: The mock UI store MUST expose the following actions:
  - `selectRole(role)`: Sets the mock role, populates mock data for that role, and returns the target redirect route
  - `clearSession()`: Resets all mock state to initial values
  - `getMockDataForRole(role)`: Returns pre-seeded realistic data appropriate for the selected role
- **FR-013**: Components and views MUST NOT use local `ref()`, `reactive()`, or ad-hoc singleton patterns for any data that is shared across multiple views. Shared state MUST flow through the Pinia store.
- **FR-014**: The mock UI store MUST NOT persist state to `localStorage` or any external storage — it operates purely in-memory and resets on page refresh.
- **FR-015**: The `useMockUiStore` MUST coexist with the existing `useAuthStore` without collision. Both stores operate independently; mock state does not interfere with real authentication tokens or user data.

#### Mock Data Quality

- **FR-020**: Mock student profiles MUST include culturally appropriate Arabic names, grade levels matching the Algerian primary system (السنة 4, السنة 5), and school names.
- **FR-021**: Mock competency data MUST include at least 3 subjects (Mathematics, Arabic, French) with 3+ competencies each, covering all mastery levels (Not Started through Mastered).
- **FR-022**: Mock pedagogical alerts MUST include at least one alert per severity level (Info, Warning, Critical) with realistic messages in Arabic.
- **FR-023**: Mock recent activity data MUST use relative timestamps computed from the current date.

### Key Entities

- **Mock Session**: A transient in-memory representation of a fake user session, containing the selected role, mock user identity, and associated mock data. Lives exclusively in the Pinia store and is not persisted.
- **Mock User**: A lightweight object conforming to the `User` interface shape (`id`, `email`, `role`, `language`) populated with plausible test data. Does not represent a real database record.
- **Mock Student Profile**: A fabricated student record with Arabic name, grade level, school, and linked competency profiles. Used to populate dashboard widgets with realistic content.
- **Mock Competency Data**: Pre-seeded competency mastery levels and BKT probability snapshots used to render radar charts, heatmaps, and progress indicators.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of landing page CTA clicks lead to a functional role-selection screen within 1 second, with no dead-end or blank views.
- **SC-002**: Users can complete the mock auth flow (CTA → role selection → dashboard) in under 5 seconds with no manual data entry.
- **SC-003**: All 3 dashboard views (Student Journey, Parent Dashboard, Expert Analytics) render with non-empty, realistic mock data after mock authentication.
- **SC-004**: Zero instances of shared state managed via local `ref()` or `reactive()` in any view — all shared state lives in the Pinia store (verifiable via code review).
- **SC-005**: The mock auth flow does not interfere with the real authentication flow — `/login` continues to function independently.
- **SC-006**: Pinia DevTools show all mock state transitions with clear, named actions for every role selection and session clear.
- **SC-007**: The mock auth route and store can be removed in a single PR without requiring changes to any production authentication code.

## Assumptions

- The backend is not yet available for real authentication during the current design/demo phase; mock auth is a temporary bridge.
- The existing Stitch mockup routes (`/parent-dashboard`, `/student/journey`, `/parent/analytics`) remain the target dashboard views for mock navigation.
- Pinia is already installed and configured in the application (confirmed: `createPinia()` in `main.ts`).
- The mock authentication view is a temporary development artifact and will be removed or gated behind a feature flag before production deployment.
- The existing `useAuthStore` and real `/login` route remain untouched — no modifications to the production auth flow are required.
- Mock data is hardcoded in the store factory functions, not fetched from any API.
- RTL layout is the default for the mock auth view, consistent with the landing page.
