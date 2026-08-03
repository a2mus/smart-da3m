---
title: Sprint Change Proposal — UX/UI Gap Analysis Remediation
project: Ihsane Platform
date: 2026-08-03
trigger: docs/ux_ui_analysis_and_gaps.md
scope: Moderate
status: approved
affected_epics: [1, 2, 6, 8, 10]
new_stories: [1.9, 10.3]
expanded_stories: [1.8, 2.3, 6.1, 8.1]
bug_fixes: 3
ux_enhancements: 5
---

# Sprint Change Proposal — UX/UI Gap Analysis Remediation

## 1. Issue Summary

### Problem Statement

A UX/UI intuitiveness evaluation conducted on 2026-08-03 across all three personas (Student, Parent, Expert) and cross-cutting concerns revealed **5 UX friction points** and **3 implementation bugs**. The evaluation was performed via user flow analysis and live browser testing against the deployed MVP.

### Discovery Context

- **When:** Post-implementation quality review (not a mid-sprint blocker)
- **How:** Persona-by-persona walkthrough + live browser testing
- **Severity:** Student persona scores lowest (6.5/10) due to lack of age-band adaptation. Parent and Expert personas score well (8/10) but have specific friction points around PIN management and content preview workflows. Three cross-cutting bugs cause runtime errors or broken flows in production.

### Evidence Summary

| Evidence | Source | Type |
|----------|--------|------|
| Year 1 student sees identical text-heavy UI as Year 5 | Live browser testing | UX gap |
| Mid-diagnostic browser close → no resume prompt | User flow analysis | UX gap |
| No PIN management modal in parent dashboard | User flow analysis | UX gap |
| Blank charts with no guidance for new parents | User flow analysis | UX gap |
| `ModuleEditor.vue` requires full modal for preview | User flow analysis | UX gap |
| Language toggle hidden inside view forms | Live browser testing | UX gap |
| `Register.vue` L53 redirects to `/parent/dashboard` (404) | Live browser testing | 🔴 Bug |
| `useI18n()` outside Vue setup context in `auth.ts` | Runtime exception | 🔴 Bug |
| `getChildrenList()` breaks on envelope response | API testing | 🔴 Bug |

---

## 2. Impact Analysis

### Epic Impact

| Epic | Impact Type | Details |
|------|------------|---------|
| **Epic 1** (Multi-Tenant Foundation) | Scope expansion + 2 bug fixes | Add Story 1.9 (PIN management modal), expand Story 1.8 AC (useI18n fix), fix Register.vue redirect in Story 1.6 |
| **Epic 2** (Diagnostic Engine) | Scope expansion | Expand Story 2.3 AC — add resume diagnostic banner to student dashboard |
| **Epic 6** (Expert Content Authoring) | Scope expansion | Expand Story 6.1 AC — add side-by-side live preview toggle to ModuleEditor |
| **Epic 8** (Parent Dashboard) | Scope expansion + 1 bug fix | Expand Story 8.1 AC — add empty state onboarding + fix getChildrenList payload |
| **Epic 10** (Bilingual Completeness) | New story | Add Story 10.3 — global language toggle in AppHeader |
| Epics 3, 4, 5, 7, 9 | **No impact** | — |

### Story Impact — Current Stories Requiring Changes

| Story | Change |
|-------|--------|
| Story 1.6 | Fix `Register.vue` redirect from `/parent/dashboard` to `/parent` |
| Story 1.8 | Add AC: fix `useI18n()` scope exception in `auth.ts` |
| Story 2.3 | Add AC: resume diagnostic banner on student dashboard |
| Story 6.1 | Add AC: side-by-side live preview toggle in `ModuleEditor.vue` |
| Story 8.1 | Add AC: empty state onboarding checklist + fix `getChildrenList()` payload normalization |

### Story Impact — New Stories

| Story | Epic | Description |
|-------|------|-------------|
| **Story 1.9** | Epic 1 | Parent PIN Management Modal |
| **Story 10.3** | Epic 10 | Global Language Toggle in App Header |

### Artifact Conflicts

- **PRD:** No conflicts. All gaps are refinements of existing FRs. Minor addendum recommended to FR-1 (PIN management UI mention) and FR-9 (resume UX expectation).
- **Architecture Spine:** No conflicts. All changes are frontend-level. The `useI18n()` fix aligns with the Architecture Spine consistency convention ("Pinia stores are the frontend's single source of truth").
- **Epics Document:** Requires update — 2 new stories added, 5 stories expanded.

### Technical Impact

- **Frontend only** — no backend schema changes, no new API endpoints (except optional `POST /api/v1/auth/children/{id}/pin` for PIN reset)
- **No infrastructure or deployment changes**
- **New i18n keys** needed for: resume banner, PIN management labels, onboarding checklist steps, language toggle labels
- **New tests** needed: Vitest unit tests for resume banner, PIN modal, empty state, language toggle, payload normalization; Playwright E2E update for registration redirect

---

## 3. Recommended Approach

### Selected Path: **Option 1 — Direct Adjustment**

All changes can be addressed by modifying existing stories and adding 2 small new stories within the current epic structure.

### Rationale

- ✅ All changes are frontend-focused, low-risk, and well-scoped
- ✅ They align with existing epics and FRs — no new architectural decisions needed
- ✅ The 3 bugs should be fixed immediately (they affect live production flows)
- ✅ The UX enhancements strengthen the pilot experience without introducing scope creep
- ✅ Total effort is manageable: ~3 days of developer work across 6 existing epics
- ✅ No rollback or MVP scope reduction is necessary

### Alternatives Considered

- **Rollback:** Not applicable — these are additive improvements, nothing needs reverting
- **MVP Review:** Not needed — MVP scope is not threatened by any of these changes

### Effort & Risk Summary

| Metric | Value |
|--------|-------|
| **Total effort** | ~3 developer days |
| **Risk level** | Low |
| **Timeline impact** | Negligible — changes can be parallelized across epics |
| **Dependency changes** | None |

---

## 4. Detailed Change Proposals

### 4.1 Bug Fixes (Priority: Immediate)

#### Proposal 1: Fix Register.vue Redirect Bug

- **Epic:** Epic 1 (Multi-Tenant Platform Foundation)
- **Story:** Story 1.6 (Self-Registration Flow for Independent Parents)
- **Change type:** Bug fix (1-line)
- **Effort:** Trivial

**Acceptance Criteria Update:**

```
Story 1.6, last acceptance criterion:

OLD:
And the parent is redirected to the parent dashboard with the
household org as active context

NEW:
And the parent is redirected to `/parent` (not `/parent/dashboard`)
with the household org as active context
And `Register.vue` Line 53 uses `router.push('/parent')` matching
the defined route
```

**Code fix:** `Register.vue` Line 53: `router.push('/parent/dashboard')` → `router.push('/parent')`

---

#### Proposal 2: Fix `useI18n()` Scope Exception in auth.ts

- **Epic:** Epic 1 (Multi-Tenant Platform Foundation)
- **Story:** Story 1.8 (Fix RBAC Enum Case Mismatch & Analytics Auth)
- **Change type:** Bug fix (scope expansion)
- **Effort:** Low (< 1 hour)

**Acceptance Criteria Addition:**

```
Story 1.8, ADD new criterion:

And the `auth.ts` store replaces `useI18n()` (which requires Vue
setup context) with `i18n.global.t` for any locale-dependent
string access outside components
```

**Code fix:** `auth.ts` — replace `useI18n()` call with `i18n.global.t` from the app's i18n singleton.

---

#### Proposal 3: Fix `getChildrenList()` Payload Handling

- **Epic:** Epic 8 (Parent Dashboard & Insights)
- **Story:** Story 8.1 (Real Dashboard API & Replace Mock dashboardService)
- **Change type:** Bug fix (scope expansion)
- **Effort:** Low (< 1 hour)

**Acceptance Criteria Addition:**

```
Story 8.1, ADD new criterion:

And `dashboardService.ts` normalizes API responses defensively:
`(response.data.items || response.data).map(...)` to handle
both envelope `{items: [...]}` and raw array `[...]` responses
```

**Code fix:** `dashboardService.ts` → `getChildrenList()`: wrap response access with `(response.data.items || response.data)`.

---

### 4.2 UX Enhancements (Priority: Sprint)

#### Proposal 4: Global Language Toggle in App Header

- **Epic:** Epic 10 (Bilingual Completeness & i18n Polish)
- **Story:** NEW Story 10.3
- **Change type:** New story
- **Effort:** Medium (half day)

**NEW Story 10.3: Global Language Toggle in App Header**

As a **user on any page**,
I want **a permanent Arabic ↔ Français toggle in the app header**,
So that **I can switch language from any screen without navigating to a settings page**.

**Acceptance Criteria:**

- **Given** the user is on any authenticated page
- **When** they view the app header (`AppHeader.vue`)
- **Then** a toggle switch labeled `العربية ↔ Français` is visible
- **And** tapping it switches locale, `dir` attribute, and all UI text instantly (per FR-28)
- **And** the toggle is visible on all screen sizes (including mobile)
- **And** the selected language persists in `localStorage`
- **And** the toggle uses logical CSS (no physical direction utilities)

---

#### Proposal 5: Diagnostic Resume Banner on Student Dashboard

- **Epic:** Epic 2 (Diagnostic Engine Reliability & Architecture Integrity)
- **Story:** Story 2.3 (Wire Diagnostic Endpoint to Engine)
- **Change type:** Expand acceptance criteria
- **Effort:** Medium (half day)

**Acceptance Criteria Addition:**

```
Story 2.3, ADD frontend criteria:

And the student dashboard (`student/Dashboard.vue`) checks for any
  active diagnostic session (status=IN_PROGRESS) on mount
And if an active session exists, a prominent "Resume Diagnostic
  (Question N/M)" banner renders at the top of the dashboard
And tapping the banner navigates to `DiagnosticRunner.vue` with
  the active session_id, resuming where the student left off
And the banner uses i18n keys: `diagnostic.resume.title`,
  `diagnostic.resume.progress`
And the banner is dismissible (student can choose to start fresh)
```

---

#### Proposal 6: Parent PIN Management Modal

- **Epic:** Epic 1 (Multi-Tenant Platform Foundation)
- **Story:** NEW Story 1.9
- **Change type:** New story
- **Effort:** Medium (1 day)

**NEW Story 1.9: Parent PIN Management Modal**

As a **parent**,
I want **to view and reset my child's 4-digit PIN from my dashboard**,
So that **I can help my child log in if they forget their PIN**.

**Acceptance Criteria:**

- **Given** the parent is on their dashboard
- **When** they tap "Manage Children & PINs" in the header/child selector
- **Then** a modal shows each child's name and current PIN (masked, with reveal toggle)
- **And** the parent can generate a new random PIN per child
- **And** the new PIN is persisted via `POST /api/v1/auth/children/{id}/pin`
- **And** the modal uses i18n keys for all labels
- **And** only the parent who "owns" the child can view/reset the PIN (enforced by RBAC + `parent_id` check)
- **And** the PIN reveal uses a temporary display (auto-hides after 5 seconds)

---

#### Proposal 7: Empty State Onboarding for New Parents

- **Epic:** Epic 8 (Parent Dashboard & Insights)
- **Story:** Story 8.1 (Real Dashboard API & Replace Mock dashboardService)
- **Change type:** Expand acceptance criteria
- **Effort:** Low-Medium (half day)

**Acceptance Criteria Addition:**

```
Story 8.1, ADD new criterion:

And when no diagnostic data exists for any child, the dashboard
  renders an onboarding checklist instead of blank charts:
  Step 1: "Give your child their PIN: [PIN]"
  Step 2: "Have them take the 10-min Math Diagnostic"
  Step 3: "Come back here to view insights"
And the checklist auto-dismisses once the first diagnostic session
  is completed
And each step uses i18n keys: `onboarding.step1`, `onboarding.step2`,
  `onboarding.step3`
And the checklist is responsive and mobile-friendly
```

---

#### Proposal 8: Live Preview Toggle in ModuleEditor

- **Epic:** Epic 6 (Expert Content Authoring & AI-Assisted Drafting)
- **Story:** Story 6.1 (Expert Module CRUD via Repository Layer)
- **Change type:** Expand acceptance criteria
- **Effort:** Medium (1 day)

**Acceptance Criteria Addition:**

```
Story 6.1, UPDATE existing criterion:

OLD:
And the `ModuleEditor.vue` view is fully functional (not a stub),
using the real `contentStore`

NEW:
And the `ModuleEditor.vue` view is fully functional (not a stub),
using the real `contentStore`
And the question builder includes a side-by-side "Live Preview"
  toggle that shows the student-facing rendering of the question
  being edited without requiring modal navigation
And the preview updates in real-time as the expert edits
And the preview renders correctly for all item types
  (multiple_choice, image_choice, numeric)
And the preview panel is collapsible to reclaim editor space
```

---

## 5. Implementation Handoff

### Change Scope Classification: **Moderate**

This change proposal involves backlog additions (2 new stories) and acceptance criteria expansions (5 existing stories) across 6 epics, plus 3 immediate bug fixes.

### Handoff Plan

| Role | Responsibility |
|------|---------------|
| **Developer agent** | Implement bug fixes (Proposals 1-3) immediately. Implement UX enhancements (Proposals 4-8) when their parent epics are active. |
| **Product Owner / Developer** | Update `epics.md` with new stories (1.9, 10.3) and expanded ACs. Update sprint-status if applicable. |
| **PM / Architect** | No action needed — no architectural or scope changes. Minor PRD addendum recommended (FR-1 PIN UI, FR-9 resume UX). |

### Implementation Sequence

1. **Immediate (bug fixes, any time):**
   - Proposal 1: Register.vue redirect (trivial, 1-line)
   - Proposal 2: auth.ts useI18n scope (low effort)
   - Proposal 3: dashboardService.ts payload (low effort)

2. **With Epic 1 sprint:**
   - Proposal 6: Story 1.9 — PIN management modal

3. **With Epic 2 sprint:**
   - Proposal 5: Story 2.3 expansion — resume banner

4. **With Epic 6 sprint:**
   - Proposal 8: Story 6.1 expansion — live preview toggle

5. **With Epic 8 sprint:**
   - Proposal 7: Story 8.1 expansion — empty state onboarding

6. **With Epic 10 sprint (or any time, independent):**
   - Proposal 4: Story 10.3 — global language toggle

### Success Criteria

- [ ] All 3 bugs fixed and verified (no 404 on register, no useI18n exception, no payload parse error)
- [ ] Resume diagnostic banner appears for students with active sessions
- [ ] Parents can view and reset child PINs from dashboard
- [ ] New parents see onboarding checklist instead of blank charts
- [ ] Language toggle accessible from app header on all pages
- [ ] ModuleEditor has functional side-by-side live preview
- [ ] All new UI text uses i18n keys (AR + FR)
- [ ] WCAG AA compliance maintained (axe-core audit passes)

---

*Generated by Correct Course workflow on 2026-08-03*
*Trigger document: `docs/ux_ui_analysis_and_gaps.md`*
