# Quickstart: Navigation Restructure & Role-Based User Experience

**Date**: 2026-04-18
**Feature**: 005-navigation-restructure
**Branch**: `005-navigation-restructure`

## Overview

This feature restructures the Ihsane platform's navigation into a clean, role-based architecture:

1. **Landing Page** (`/`) — Public welcome page with CTAs for sign-up and sign-in
2. **Sign-In** (`/login`) — Role-picker → role-specific auth form (email+password, social, or parent-email+PIN)
3. **Registration** (`/register`) — New parent/expert account creation with social signup support
4. **Parent Dashboard** (`/parent`) — Mobile-first child progress monitoring
5. **Student Dashboard** (`/student`) — Age-adapted learning journey interface
6. **Expert Dashboard** (`/expert`) — Desktop-optimized content management workspace

## Prerequisites

- Docker Compose running (`docker compose up -d`)
- Node.js 18+ and npm
- Python 3.11+ with venv
- Google OAuth credentials (Cloud Console)
- Facebook OAuth credentials (Developer Portal)

## Environment Variables (NEW)

Add to `backend/.env`:
```env
# Social OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
OAUTH_REDIRECT_BASE=http://localhost:8000/api/v1/auth/oauth
FRONTEND_URL=http://localhost:5173
```

## Database Migration

```bash
cd backend
alembic revision --autogenerate -m "add display_name grade_level social_accounts"
alembic upgrade head
```

## New Dependencies

**Backend** (add to `requirements.txt`):
```
authlib>=1.3.0
httpx>=0.27.0  # already present
```

**Frontend** (no new npm packages needed — social auth handled via backend redirect).

## Development Workflow

### 1. Run backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run frontend
```bash
cd frontend
npm run dev
```

### 3. Test the flow
1. Navigate to `http://localhost:5173/` → see landing page
2. Click "Sign In" → see role picker
3. Select "Parent" → see email+password form + Google/Facebook buttons
4. Select "Student" → see parent email + PIN form
5. Sign in → redirected to role-specific dashboard

## Key Files Modified

### Backend
| File | Change |
|------|--------|
| `app/models/user.py` | Add `display_name`, `grade_level` |
| `app/models/social_account.py` | NEW — SocialAccount model |
| `app/schemas/user.py` | Add `display_name`, `grade_level`, social auth schemas |
| `app/api/endpoints/auth.py` | Add OAuth endpoints, modify PIN login, add PIN regeneration |
| `app/core/config.py` | Add OAuth config vars |
| `requirements.txt` | Add `authlib` |

### Frontend
| File | Change |
|------|--------|
| `src/router/index.ts` | Clean routes, add register/callback, remove Stitch routes |
| `src/views/LandingPage.vue` | Redesign as authoritative landing page |
| `src/views/Login.vue` | Add role picker, social buttons, parent-email field |
| `src/views/Register.vue` | NEW — Registration with social signup |
| `src/views/AuthCallback.vue` | NEW — OAuth callback token handler |
| `src/views/parent/Dashboard.vue` | Build full functional dashboard |
| `src/views/parent/Analytics.vue` | NEW — Detailed child analytics |
| `src/views/parent/Children.vue` | NEW — Manage children + PIN regeneration |
| `src/views/student/Dashboard.vue` | Build full functional dashboard |
| `src/views/expert/Dashboard.vue` | Build full functional dashboard |
| `src/stores/auth.ts` | Add `loginWithSocial`, `loginWithPin` (email+pin), `regeneratePin` |
| `src/services/api.ts` | Add social auth, PIN regeneration API calls |

### Deleted Files
| File | Reason |
|------|--------|
| `src/views/Home.vue` | Merged into LandingPage.vue |
| `src/views/ParentDashboard.vue` | Stitch mockup → replaced by `parent/Dashboard.vue` |
| `src/views/AnalyticsView.vue` | Stitch mockup → replaced by `parent/Analytics.vue` |
| `src/views/StudentJourney.vue` | Stitch mockup → replaced by `student/Dashboard.vue` |
| `src/services/mockUiState.ts` | Spec 004 artifact, superseded |
