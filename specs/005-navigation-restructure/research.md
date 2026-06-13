# Research: Navigation Restructure & Role-Based User Experience

**Date**: 2026-04-18
**Feature**: 005-navigation-restructure

## R-001: Social Authentication Strategy (Google, Facebook)

**Decision**: Use OAuth 2.0 Authorization Code Flow via `authlib` (Python) on the backend, handling callback and token exchange server-side. The frontend initiates the flow by redirecting to a backend-generated auth URL.

**Rationale**: Keeping the OAuth flow server-side avoids exposing client secrets in the SPA bundle. `authlib` is the most mature Python OAuth library, supports FastAPI natively, and handles both Google and Facebook with minimal configuration. The alternative (frontend-only with `@react-oauth/google` or Firebase) would add Firebase as a dependency and complicate the existing JWT infrastructure.

**Alternatives considered**:
- `python-social-auth`: Heavier, Django-oriented, excessive for two providers.
- Firebase Auth: Would replace the existing JWT system entirely — too invasive for this feature.
- Frontend-only OAuth (Google Identity Services): Exposes client secrets, requires CORS workarounds.

**Implementation pattern**:
1. Backend defines `GET /auth/oauth/{provider}/authorize` → returns redirect URL to Google/Facebook.
2. Provider redirects to `GET /auth/oauth/{provider}/callback` → backend exchanges code for profile, upserts user, returns JWT tokens.
3. Frontend opens the authorize URL in same window (full redirect, not popup) for mobile compatibility.
4. New env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`.
5. New backend dependency: `authlib>=1.3.0`.

## R-002: Student PIN Login — Parent Email as Lookup Key

**Decision**: Modify the `StudentPinLogin` schema to accept `parent_email` + `pin_code`. The backend looks up the parent by email, then finds the matching child via `parent_id` and verifies the PIN.

**Rationale**: The current `login/pin` endpoint iterates ALL students and brute-force checks PINs — this is O(n) and doesn't scale. Adding `parent_email` scopes the lookup to a single parent's children, making it O(1) database lookup + O(k) PIN checks where k is small (number of children per parent).

**Alternatives considered**:
- Keep PIN-only lookup: Doesn't scale, no parent scoping, security risk.
- Use unique auto-generated codes instead of email+PIN: Adds user friction, harder for children to remember.

## R-003: Social Account Linking Strategy

**Decision**: Link social accounts to existing email+password accounts by matching on email address. If a user registers via email first, then later uses Google sign-in with the same email, the accounts are merged automatically. The user can then sign in via either method.

**Rationale**: Email-based matching is the simplest and most intuitive approach. Users expect that their Google account (which uses their email) should connect to their existing account. This avoids duplicate account creation.

**Implementation pattern**:
1. New model: `SocialAccount` table linking `user_id` to `provider` + `provider_user_id`.
2. On OAuth callback: check if email exists in `users` → link if found, else create new user.
3. `User` model gets nullable `display_name` field (populated from social profile or registration form).

## R-004: Landing Page Performance Target (< 3s Critical Content)

**Decision**: Use Vue's async component loading with priority hints. The hero section and CTA buttons are part of the main bundle (no lazy loading). Secondary sections (features, how-it-works, testimonials) use `defineAsyncComponent` with `Suspense` for deferred loading.

**Rationale**: The spec requires critical content within 3 seconds. Budget devices on 3G in Algeria need a small initial payload. The hero + CTA is ~5KB of HTML/CSS. Secondary content can load progressively.

**Alternatives considered**:
- SSR with Nuxt: Too invasive an architecture change for this feature.
- Static pre-rendering: Would break the dynamic authenticated-user redirect logic.

## R-005: PIN Regeneration UX Flow

**Decision**: Parent Dashboard includes a "Manage PIN" button next to each child. Clicking it shows a confirmation dialog, generates a new 4-6 digit PIN client-side, and sends it to `POST /auth/children/{child_id}/regenerate-pin`. The new PIN is displayed once with a "Copy" button and instruction text.

**Rationale**: Simple, parent-controlled flow that requires no child interaction. The parent can share the new PIN in person. No email flow needed since the parent is already authenticated.

## R-006: Route Cleanup — Stitch Mockup Removal

**Decision**: Remove the following Stitch-era routes and their view files:
- `/parent-dashboard` → `StitchParentDashboard` → `ParentDashboard.vue` (root views/)
- `/parent/analytics` → `StitchAnalyticsView` → `AnalyticsView.vue` (root views/)
- `/student/journey` → `StitchStudentJourney` → `StudentJourney.vue` (root views/)

Replace with:
- `/parent/analytics` → re-register under auth guard, pointing to `views/parent/Analytics.vue`
- `/student` → already exists, Dashboard.vue is production view

Additionally: `Home.vue` (commented out) will be deleted — its functionality merged into `LandingPage.vue`.

**Rationale**: The spec explicitly states these routes are consolidated. Keeping dead Stitch routes creates confusion and bloats the bundle.

## R-007: Mock Auth State (Spec 004) Removal

**Decision**: Remove `mockUiState.ts` service and any `useMockUiStore` references. The mock data currently in `mockUiState.ts` will be repurposed into a dedicated `mockData/` directory used by dashboard components during the pilot phase (until real API data is available).

**Rationale**: Spec 005 supersedes 004. Mock auth routing is replaced by real auth. However, mock dashboard DATA is still needed for pilot demos — just decoupled from the auth flow.
