# API Contracts: Authentication & User Management

**Date**: 2026-04-18
**Feature**: 005-navigation-restructure
**Base URL**: `/api/v1`

---

## Auth Endpoints

### POST /auth/login/email (MODIFY)

**Change**: No schema change. Existing endpoint works as-is for Parent/Expert email+password login.

**Request**:
```json
{
  "email": "parent@example.com",
  "password": "securepass123"
}
```

**Response 200**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Response 401**: `{ "detail": "Invalid email or password" }`

---

### POST /auth/login/pin (MODIFY)

**Change**: Add `parent_email` field to scope PIN lookup to a specific parent's children.

**Request (NEW schema)**:
```json
{
  "parent_email": "parent@example.com",
  "pin_code": "1234"
}
```

**Response 200**: Same Token schema as email login.

**Response 401**: `{ "detail": "Invalid PIN code" }`

**Response 429** (NEW): `{ "detail": "Too many attempts. Try again in 15 minutes." }`

---

### GET /auth/oauth/{provider}/authorize (NEW)

**Description**: Initiates OAuth flow. Returns URL to redirect the user to the provider's consent screen.

**Path params**: `provider` ∈ `["google", "facebook"]`

**Query params**:
- `role`: `"PARENT"` | `"EXPERT"` (required — determines role on first-time signup)
- `redirect_uri`: Frontend URL to return to after callback (optional, defaults to `/login`)

**Response 200**:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=...&scope=email+profile&state=..."
}
```

---

### GET /auth/oauth/{provider}/callback (NEW)

**Description**: OAuth callback endpoint. Exchanges authorization code for user profile, upserts user, returns JWT tokens. Redirects browser to frontend with tokens in URL fragment.

**Query params** (from provider):
- `code`: Authorization code
- `state`: CSRF state token

**Response 302**: Redirects to `{frontend_url}/auth/callback#access_token=...&refresh_token=...&token_type=bearer`

**Error 302**: Redirects to `{frontend_url}/login?error=oauth_failed&provider={provider}`

---

### POST /auth/register/parent (MODIFY)

**Change**: Add `display_name` field.

**Request (NEW schema)**:
```json
{
  "email": "newparent@example.com",
  "password": "securepass123",
  "display_name": "أحمد بن محمد",
  "language": "AR"
}
```

**Response 201**: UserResponse with new `display_name` and `id`.

---

### POST /auth/register/student (MODIFY)

**Change**: Add `display_name` and `grade_level` fields.

**Request (NEW schema)**:
```json
{
  "parent_id": "uuid-here",
  "pin_code": "1234",
  "display_name": "ياسمين",
  "grade_level": 3
}
```

**Response 201**: UserResponse with child info.

---

### POST /auth/children/{child_id}/regenerate-pin (NEW)

**Description**: Parent regenerates a child's PIN code. Requires parent authentication. The child must belong to the authenticated parent.

**Auth**: Bearer token (role=PARENT)

**Path params**: `child_id` — UUID of the child user

**Response 200**:
```json
{
  "child_id": "uuid-here",
  "new_pin": "5678",
  "message": "PIN regenerated successfully. Share this new PIN with your child."
}
```

**Response 403**: `{ "detail": "You can only manage your own children" }`
**Response 404**: `{ "detail": "Child not found" }`

---

### GET /auth/me (NO CHANGE)

**Response 200** (updated UserResponse):
```json
{
  "id": "uuid-here",
  "email": "parent@example.com",
  "role": "PARENT",
  "language": "AR",
  "display_name": "أحمد بن محمد",
  "parent_id": null,
  "grade_level": null,
  "created_at": "2026-04-18T10:00:00Z"
}
```

---

## Frontend Route Contracts

### Public Routes (no auth required)

| Route | Name | Component | Meta |
|-------|------|-----------|------|
| `/` | `LandingPage` | `views/LandingPage.vue` | `public: true, guestOnly: true` |
| `/login` | `Login` | `views/Login.vue` | `public: true, guestOnly: true` |
| `/register` | `Register` | `views/Register.vue` (NEW) | `public: true, guestOnly: true` |
| `/auth/callback` | `AuthCallback` | `views/AuthCallback.vue` (NEW) | `public: true` |

### Parent Routes (role=PARENT)

| Route | Name | Component | Meta |
|-------|------|-----------|------|
| `/parent` | `ParentDashboard` | `views/parent/Dashboard.vue` | `requiresAuth, roles: [PARENT]` |
| `/parent/analytics` | `ParentAnalytics` | `views/parent/Analytics.vue` (NEW) | `requiresAuth, roles: [PARENT]` |
| `/parent/children` | `ManageChildren` | `views/parent/Children.vue` (NEW) | `requiresAuth, roles: [PARENT]` |

### Student Routes (role=STUDENT)

| Route | Name | Component | Meta |
|-------|------|-----------|------|
| `/student` | `StudentDashboard` | `views/student/Dashboard.vue` | `requiresAuth, roles: [STUDENT]` |
| `/student/diagnostic` | `DiagnosticSession` | `views/student/DiagnosticSession.vue` | `requiresAuth, roles: [STUDENT]` |
| `/student/remediation` | `RemediationSession` | `views/student/RemediationSession.vue` | `requiresAuth, roles: [STUDENT]` |

### Expert Routes (role=EXPERT)

| Route | Name | Component | Meta |
|-------|------|-----------|------|
| `/expert` | `ExpertDashboard` | `views/expert/Dashboard.vue` | `requiresAuth, roles: [EXPERT]` |
| `/expert/modules` | `ModuleList` | `views/expert/ModuleList.vue` | `requiresAuth, roles: [EXPERT]` |
| `/expert/modules/:id/edit` | `ModuleEditor` | `views/expert/ModuleEditor.vue` | `requiresAuth, roles: [EXPERT]` |
| `/expert/analytics` | `ExpertAnalytics` | `views/expert/Analytics.vue` | `requiresAuth, roles: [EXPERT]` |

### Removed Routes

| Old Route | Old Name | Action |
|-----------|----------|--------|
| `/parent-dashboard` | `StitchParentDashboard` | DELETE |
| `/parent/analytics` (public) | `StitchAnalyticsView` | REPLACE with auth-guarded version |
| `/student/journey` | `StitchStudentJourney` | DELETE |
