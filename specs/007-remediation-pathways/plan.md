# Implementation Plan: Remediation Pathways (Parcours de Remédiation)

**Branch**: `007-remediation-pathways` | **Date**: 2026-06-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-remediation-pathways/spec.md`

## Summary

Implement the student-facing remediation session UI in Vue 3. The backend remediation engine (DynamicDifficultyAdjuster, StudentEngagementTracker, PathwayGenerator, PassportEvaluator, RemediationEngine) and all five API endpoints are fully implemented. This plan covers the frontend work: enhancing the existing stub components, creating new presentational components (DifficultyMeter, PathwayOverview), wiring up the route with a `:competencyId` param, adding i18n strings under a `remediation` namespace, and integrating the adaptive feedback loop (difficulty meter animation, engagement recommendation banners, conditional atom progression, Passport assessment with badge awarding).

## Technical Context

**Language/Version**: TypeScript 5.x + Vue 3.5+ (Composition API, `<script setup>`)
**Primary Dependencies**: Vue 3, vue-router, vue-i18n, Tailwind CSS (utility classes: `bg-warm-*`, `text-primary-*`, `rounded-2xl`, `shadow-soft`), Axios (via `api.ts`)
**Storage**: N/A (all state is server-driven via API; offline caching deferred)
**Testing**: Vitest (frontend)
**Target Platform**: Modern web browsers (Chrome, Firefox, Edge, Safari), RTL-first (Arabic + French)
**Performance Goals**: Pathway view render < 500ms, atom completion UI update < 500ms after API response, touch targets ≥ 60px

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **System Architecture**: Vue 3 SPA consuming FastAPI backend monolith [PASS]
- **Technology Stack**: Vue 3 / Vite + TypeScript + Tailwind CSS [PASS]
- **Dependency Threshold**: No new frontend dependencies needed; all UI is custom-built with existing stack [PASS]
- **Testing**: Vitest for component/service tests [PASS]
- **Design System**: Nurturing Soft Modernism — `bg-warm-*`, `text-primary-*`, `rounded-2xl`, `shadow-soft` [PASS]
- **Accessibility**: RTL-first via CSS logical properties, 60px touch targets for all interactive elements [PASS]
- **Security**: JWT token via `api.ts` interceptors, RBAC route guards for STUDENT role [PASS]

## Project Structure

### Documentation (this feature)

```text
specs/007-remediation-pathways/
├── plan.md              # This file
├── research.md          # Phase 0 output (if needed)
├── data-model.md        # Phase 1 output (if needed)
├── quickstart.md        # Phase 1 output (if needed)
├── contracts/           # Phase 1 output (if needed)
└── tasks.md             # Phase 2 output
```

### Source Code (frontend only — backend is complete)

```text
frontend/src/
├── components/
│   └── student/
│       ├── KnowledgeAtom.vue          # MODIFY — adaptive feedback, DifficultyMeter, media player
│       ├── PassportAssessment.vue     # MODIFY — edge cases, RTL, accessibility, retry flow
│       ├── PathwayOverview.vue        # CREATE — atom sequence with locked/available/completed states
│       └── DifficultyMeter.vue        # CREATE — segmented bar 1–10 with animated transitions
├── locales/
│   ├── fr.json                        # MODIFY — add `remediation` namespace
│   └── ar.json                        # MODIFY — add `remediation` namespace
├── router/
│   └── index.ts                       # MODIFY — add `:competencyId` param to remediation route
├── services/
│   └── remediationService.ts          # MODIFY — add types/interfaces for new components, edge-case helpers
├── views/
│   └── student/
│       └── RemediationSession.vue     # MODIFY — full session orchestrator (pathway fetch, atom selection, Passport gate)
└── __tests__/                         # CREATE — Vitest tests for new/enhanced components
    ├── KnowledgeAtom.test.ts
    ├── PassportAssessment.test.ts
    ├── PathwayOverview.test.ts
    └── DifficultyMeter.test.ts
```

## Files to Create

### 1. `frontend/src/components/student/PathwayOverview.vue`
**Purpose**: Renders the full pathway atom sequence as a vertical (mobile) or horizontal (desktop) list of atom cards. Each card shows the remediation type icon (🎬/🎮/🧠), title, description, and status (🔒 locked, ▶ available, ✓ completed). Strictly enforces conditional progression — only the first uncompleted atom is clickable. Includes a `PathwayProgressBar` showing `atoms_completed / total_atoms` as an animated progress bar with fraction text. Displays the "Take Passport Assessment" CTA when `can_take_passport` is true.

**Props**: `pathway: RemediationPath`, `canTakePassport: boolean`
**Emits**: `select-atom(atomId: string)`, `take-passport()`

### 2. `frontend/src/components/student/DifficultyMeter.vue`
**Purpose**: Presentational component displaying the current difficulty level (1–10) as a segmented bar. Receives `currentDifficulty` and `previousDifficulty` as props. Animates from old to new value via CSS transitions. Color-coded segments: green (1–3), amber (4–7), red (8–10). Used inside `KnowledgeAtom.vue`.

**Props**: `currentDifficulty: number`, `previousDifficulty: number`
**No emits** — purely presentational.

### 3. `frontend/src/__tests__/KnowledgeAtom.test.ts`
### 4. `frontend/src/__tests__/PassportAssessment.test.ts`
### 5. `frontend/src/__tests__/PathwayOverview.test.ts`
### 6. `frontend/src/__tests__/DifficultyMeter.test.ts`
**Purpose**: Vitest unit tests covering component rendering, user interactions (atom selection, answer submission), edge cases (empty atoms, zero questions, network error retry), RTL rendering, and accessibility (touch target sizing). Test files are scaffolded alongside implementation.

## Files to Modify

### 7. `frontend/src/views/student/RemediationSession.vue`
**Purpose**: Full session orchestrator (currently a 16-line shell). On mount, extracts `competencyId` from route params and `studentGroup` from auth store, then fetches the pathway via `remediationService.getPathway()`. Manages session state: `currentView` ('overview' | 'atom' | 'passport' | 'results'), `activeAtom`, `pathway`, `canTakePassport`. Orchestrates transitions between views:
- **Overview**: Shows `PathwayOverview` for atom selection
- **Atom**: Shows `KnowledgeAtom` for the selected atom; on completion, fetches updated pathway state and auto-advances or returns to overview
- **Passport**: Shows `PassportAssessment` when student clicks "Take Passport"
- **Results**: Passport results with badge/retry flow

Handles edge cases: zero atoms (empty state with teacher-notification message), network errors (toast + manual retry), session expiry (401 → redirect to login with `competencyId` preserved in query).

### 8. `frontend/src/components/student/KnowledgeAtom.vue`
**Purpose**: Enhanced atom interaction component (currently 133 lines with basic stub). Additions:
- **Media player for AUDIO_VISUAL type**: Renders `atom.content.media_url` in an `aspect-video` container with native `<video>` controls and Arabic/French captions (`<track>` elements).
- **Enhanced SIMULATION interaction**: Draggable blocks (use native HTML drag-and-drop or pointer events) with visual feedback — highlight on hover, snap animation on correct placement, shake on incorrect. Each drag/tap increments `interactions`.
- **Enhanced MIND_MAP**: Concept nodes rendered as an expandable tree with animated SVG connections appearing progressively as the student taps nodes.
- **DifficultyMeter integration**: Receives `previousDifficulty` and `currentDifficulty` as props (from parent `RemediationSession` after API response), renders `DifficultyMeter` with animated transition.
- **Engagement recommendation banner** (FR-008): Dismissible banner styled based on recommendation type:
  - Frustration: amber background, 💆 icon, "Take a break" button opening a 30-second breathing timer
  - Boredom: green background, 🚀 icon, encouragement text
  - Neutral: no banner
- **Network error retry**: On `completeAtom` API failure, retries once automatically; on second failure, shows error toast with manual "Retry" button.
- **Auto-advance**: On completion, after 2-second checkmark animation, emits `complete` event. Parent handles navigation to next atom.

**Props** (existing + new): `atom`, `isCompleted`, `progressPercent`, `previousDifficulty`, `currentDifficulty`
**Emits**: `complete(timeMs, interactions, isCorrect)`, `request-break()`

### 9. `frontend/src/components/student/PassportAssessment.vue`
**Purpose**: Enhanced Passport assessment component (currently 236 lines with solid foundation). Additions:
- **Rapid-click prevention**: Submit button disabled on first click with spinner (already partially present) — ensure `isSubmitting` guard covers all paths.
- **Session expiry handling**: Detect 401 response from evaluate endpoint → preserve `currentIndex` and `answers` in session storage → emit `session-expired` event. Parent (`RemediationSession`) redirects to login.
- **Zero questions edge case**: When API returns `questions: []`, show empty state with "Assessment questions are being prepared" message and retry button.
- **Retry flow enhancement**: On fail, "Retry" button calls `loadQuestions()` again (already present). Ensure a fresh `assessment_id` is used if the API provides it.
- **Alert banner**: When `results.alert_triggered === true`, show a banner informing the student that parents/experts have been notified.
- **Mastery level transition arrow**: Animate the previous → new mastery level display with a directional arrow and color change (green for advancement, amber for regression).
- **RTL & accessibility**: Ensure all layout uses CSS logical properties, question option buttons have `min-h-[60px]`, progress bar animates correctly in RTL.

**Props**: (none — self-contained, reads `competencyId` from route)
**Emits**: `session-expired()`, `assessment-complete(results: PassportEvaluation)`

### 10. `frontend/src/services/remediationService.ts`
**Purpose**: Minor enhancements to the existing service (111 lines, all 5 API methods already present):
- Add `RemediationStatus` interface (for `getStatus()` response shape — currently inline-typed).
- Add `RecommendationType` enum or union type for engagement recommendation handling in `KnowledgeAtom`.
- Add retry logic helper method or document that components handle retry at the UI level (per spec: one automatic retry, then manual).
- Ensure all response types are fully exported for component consumption.

### 11. `frontend/src/router/index.ts`
**Purpose**: Update the remediation route to accept a `competencyId` param (FR-013):
- Change path from `/student/remediation` to `/student/remediation/:competencyId`
- The `competencyId` route param drives all API calls in `RemediationSession.vue` and `PassportAssessment.vue`

### 12. `frontend/src/locales/fr.json`
**Purpose**: Add `remediation` namespace with all French strings for:
- Pathway title, atom type labels (audio-visual, simulation, mind map), locked/available/completed status labels
- Completion messages, difficulty labels (1–10 descriptions), engagement messages (frustration, boredom, neutral)
- Passport labels (question X of Y, accuracy, previous/new level, badge earned, retry, finish)
- Empty states (zero atoms, zero questions), error messages (network failure, session expired)

### 13. `frontend/src/locales/ar.json`
**Purpose**: Same as `fr.json` but in Arabic, ensuring all strings are culturally appropriate for Algerian primary students. RTL-compatible placeholder text and labels.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No violations present. All work uses existing stack conventions — Vue 3 `<script setup>`, TypeScript, vue-i18n, Tailwind CSS, Vitest. No new dependencies required.)*

## Implementation Order (Recommended)

1. **i18n** — `fr.json` and `ar.json`: strings needed by all components come first
2. **Router** — `index.ts`: add `:competencyId` param so all components can read it
3. **Service** — `remediationService.ts`: finalize types/interfaces
4. **DifficultyMeter** — new presentational component (no API deps, testable in isolation)
5. **PathwayOverview** — new component (depends on service types + i18n)
6. **KnowledgeAtom** — enhance existing (depends on DifficultyMeter + i18n)
7. **PassportAssessment** — enhance existing (depends on i18n + edge-case handling)
8. **RemediationSession** — enhance existing shell (orchestrator, depends on all above)
9. **Tests** — Vitest tests for all components (can be written alongside each component)
