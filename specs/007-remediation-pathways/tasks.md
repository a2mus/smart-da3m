# Tasks: Remediation Pathways (Parcours de Remédiation)

**Input**: Design documents from `/specs/007-remediation-pathways/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Vitest component tests are included in Phase 5 (Verification). The backend remediation engine (DynamicDifficultyAdjuster, StudentEngagementTracker, PathwayGenerator, PassportEvaluator, RemediationEngine) and all five API endpoints are fully implemented — this feature is frontend-only.

**Organization**: Tasks are grouped by implementation phase following the dependency chain: i18n strings → route param → service types → presentational components → enhanced components → session orchestrator → verification.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1: Setup (i18n, Router, Service)

**Purpose**: Foundation that all components depend on — i18n strings, route parameter, and typed service interfaces

- [ ] T001 [P] Add `remediation` namespace with all French strings (pathway labels, atom types, difficulty, engagement messages, Passport labels, empty states, errors) in `frontend/src/locales/fr.json`
- [ ] T002 [P] Add `remediation` namespace with all Arabic strings (culturally appropriate for Algerian primary students, RTL-compatible) in `frontend/src/locales/ar.json`
- [ ] T003 [P] Update remediation route to accept `:competencyId` param: change path from `/student/remediation` to `/student/remediation/:competencyId` in `frontend/src/router/index.ts`
- [ ] T004 [P] Finalize types/interfaces (`RemediationStatus`, `RecommendationType`, exported response shapes) and add retry logic documentation in `frontend/src/services/remediationService.ts`

**Checkpoint**: i18n strings available, route wired with `competencyId`, service types exported — components can now be built

---

## Phase 2: Pathway Overview Component

**Purpose**: New presentational components that display the remediation pathway and difficulty level

- [ ] T005 Create `DifficultyMeter.vue` — segmented bar (1–10) with green/amber/red color coding, animated CSS transitions from `previousDifficulty` to `currentDifficulty`, pure presentational (no emits) in `frontend/src/components/student/DifficultyMeter.vue`
- [ ] T006 Create `PathwayOverview.vue` — vertical/horizontal atom sequence with type icons (🎬/🎮/🧠), locked/available/completed status badges, conditional progression enforcement (only first uncompleted atom clickable), `PathwayProgressBar` with animated fraction, "Take Passport Assessment" CTA when `canTakePassport` is true in `frontend/src/components/student/PathwayOverview.vue`

**Checkpoint**: Pathway visualisation and difficulty meter are independently testable

---

## Phase 3: Knowledge Atom Enhancement

**Purpose**: Upgrade the existing `KnowledgeAtom.vue` stub with adaptive feedback, media support, and engagement features

- [ ] T007 Enhance `KnowledgeAtom.vue` — add media player for AUDIO_VISUAL type (native `<video>` with `<track>` captions), draggable blocks for SIMULATION type (snap/shake animations), expandable animated SVG tree for MIND_MAP type, integrate `DifficultyMeter` with `previousDifficulty`/`currentDifficulty` props in `frontend/src/components/student/KnowledgeAtom.vue`
- [ ] T008 Add engagement recommendation banner (FR-008) — dismissible banners for frustration (amber, 💆, 30s breathing timer), boredom (green, 🚀, encouragement), neutral (hidden); network error retry (one auto-retry then manual "Retry" button); 2-second checkmark auto-advance on completion in `frontend/src/components/student/KnowledgeAtom.vue`

**Checkpoint**: All three atom interaction modes (audio-visual, simulation, mind map) are functional with adaptive feedback

---

## Phase 4: Remediation Session Wiring

**Purpose**: Enhance `PassportAssessment.vue` edge cases and wire the full session orchestrator in `RemediationSession.vue`

- [ ] T009 Enhance `PassportAssessment.vue` — rapid-click prevention (`isSubmitting` guard on all paths), session expiry detection (persist `currentIndex`/`answers` to sessionStorage on 401, emit `session-expired`), zero-questions empty state with retry, mastery level transition arrow (green up / amber down), alert banner when `results.alert_triggered === true`, RTL accessibility audit (CSS logical properties, `min-h-[60px]` touch targets) in `frontend/src/components/student/PassportAssessment.vue`
- [ ] T010 Enhance `RemediationSession.vue` — full session orchestrator: extract `competencyId` from route params + `studentGroup` from auth store, fetch pathway via `remediationService.getPathway()`, manage `currentView` state machine (overview → atom → passport → results), orchestrate transitions between `PathwayOverview` / `KnowledgeAtom` / `PassportAssessment`, handle edge cases (zero atoms empty state with teacher-notification message, network error toast + manual retry, 401 → redirect to login with `competencyId` preserved in query params) in `frontend/src/views/student/RemediationSession.vue`

**Checkpoint**: Full remediation session flow works end-to-end — pathway selection → atom completion → Passport assessment → results

---

## Phase 5: Verification

**Purpose**: Vitest component tests and integration validation

- [ ] T011 [P] Write Vitest unit tests for new components: `DifficultyMeter.test.ts` (rendering, color coding, animation triggers), `PathwayOverview.test.ts` (locked/available/completed states, conditional progression, CTA visibility) in `frontend/src/__tests__/`
- [ ] T012 [P] Write Vitest unit tests for enhanced components: `KnowledgeAtom.test.ts` (media player rendering, drag-and-drop simulation, engagement banner states, retry flow, auto-advance), `PassportAssessment.test.ts` (rapid-click guard, session expiry, zero questions, mastery transition, RTL rendering, touch target sizing) in `frontend/src/__tests__/`

**Checkpoint**: All components have passing tests covering rendering, interactions, edge cases, RTL, and accessibility

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately; all four tasks can run in parallel
- **Phase 2 (Pathway Overview)**: Depends on Phase 1 completion (needs i18n strings + service types)
- **Phase 3 (Knowledge Atom)**: Depends on Phase 2 (needs `DifficultyMeter` component) + Phase 1 (i18n)
- **Phase 4 (Session Wiring)**: Depends on Phases 2 & 3 (needs `PathwayOverview`, `KnowledgeAtom`, `PassportAssessment`)
- **Phase 5 (Verification)**: Depends on all implementation phases being complete

### Parallel Opportunities

- All Phase 1 tasks (T001–T004) can run in parallel (different files)
- T005 (`DifficultyMeter`) and T006 (`PathwayOverview`) could partially overlap since `DifficultyMeter` has no dependencies on `PathwayOverview`
- T007 and T008 are sequential on the same file (`KnowledgeAtom.vue`)
- T011 and T012 can run in parallel once implementation is complete

---

## Implementation Strategy

### Recommended Order

1. **Complete Phase 1** — i18n strings must be done first so all components can reference them
2. **Complete Phase 2** — `DifficultyMeter` and `PathwayOverview` are self-contained presentational components, ideal for building confidence
3. **Complete Phase 3** — `KnowledgeAtom` is the most complex component; build interaction modes first (T007), then adaptive feedback (T008)
4. **Complete Phase 4** — `PassportAssessment` edge cases (T009) then wire everything together in `RemediationSession` (T010)
5. **Complete Phase 5** — write all tests and validate the full flow

### Validation Checkpoints

After each phase, verify:
- **Phase 1**: `npm run dev` loads without errors; route `/student/remediation/123` resolves; i18n keys exist in both locales
- **Phase 2**: `DifficultyMeter` renders in isolation with test props; `PathwayOverview` renders with mock pathway data
- **Phase 3**: Each atom interaction mode works against mock data; engagement banner appears/disappears correctly
- **Phase 4**: Full session flow: overview → select atom → complete atom → passport → results
- **Phase 5**: `npm run test` passes all 4 test files with ≥ 80% coverage on new/enhanced components
