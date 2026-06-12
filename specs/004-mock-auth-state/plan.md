# Plan: Mock Authentication Flow & UI State Architecture

**Feature**: 004-mock-auth-state
**Tier**: STANDARD (frontend-only, follows existing patterns)
**Input**: spec.md at `specs/004-mock-auth-state/spec.md`

## Summary

Implement a mock authentication layer using a Pinia store (`useMockUiStore`) and a role-selection view (`/mock-auth`) that bridges the landing page to dashboard views. The existing `mockUiState.ts` service is replaced with the Pinia store for centralized state management.

## Architecture

```
LandingPage (/) ──CTA click──▶ /mock-auth (role selection)
                                    │
                          ┌─────────┼─────────┐
                          ▼         ▼         ▼
                    STUDENT    PARENT    EXPERT
                    /student/  /parent-  /parent/
                    journey    dashboard analytics
```

## Files to Create

| File | Purpose |
|------|---------|
| `src/stores/mockUiStore.ts` | Pinia store: mock session, role, user, students, alerts, competency data |
| `src/views/MockAuth.vue` | Role selection UI: 3 cards (Student/Parent/Expert) with "Nurturing Soft Modernism" design |

## Files to Modify

| File | Change |
|------|--------|
| `src/router/index.ts` | Add `/mock-auth` route + mock auth navigation guard |
| `src/views/LandingPage.vue` | Change CTA `startNow()` from `/login` → `/mock-auth` |
| `src/views/ParentDashboard.vue` | Add "Change Role" button (bottom) |
| `src/views/StudentJourney.vue` | Add "Change Role" button (bottom) |
| `src/views/AnalyticsView.vue` | Add "Change Role" button (bottom) |

## State Shape (`useMockUiStore`)

```typescript
// State
currentMockRole: 'STUDENT' | 'PARENT' | 'EXPERT' | null
mockUser: User | null
mockStudents: MockStudentProfile[]
mockAlerts: MockAlert[]
mockCompetencyData: Record<string, CompetencyProfile>

// Computed
isMockAuthenticated: boolean (derived from currentMockRole !== null)

// Actions
selectRole(role) → populates all mock data for role, returns redirect route name
clearSession() → resets all state to null/empty
```

## Router Guard Logic

Add to `router.beforeEach`:
- If route requires mock auth (check `meta.requiresMockAuth`) and user is not mock-authenticated → redirect to `/mock-auth`
- Dashboard mockup routes (`/parent-dashboard`, `/student/journey`, `/parent/analytics`) get `meta: { requiresMockAuth: true }`
- If already mock-authenticated and navigating to `/mock-auth` → redirect to current role's dashboard
- If already mock-authenticated and on landing page clicking CTA → skip `/mock-auth`, go directly to dashboard

## Dependencies

- Pinia (already installed, `createPinia()` in `main.ts`)
- Vue Router (already configured)
- Existing types: `UserRole`, `User` from `@/types/auth` and `@/stores/auth`
- Existing models: `stitchMockups.ts`

## Design Constraints

- "Nurturing Soft Modernism": warm tones, semantic tokens, asymmetric borders, RTL-first
- No `#ffffff` or `#000000` — use semantic tokens only
- Bilingual labels (Arabic primary, French secondary)
- Touch targets ≥ 44px
