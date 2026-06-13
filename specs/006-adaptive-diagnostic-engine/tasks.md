# Tasks: Adaptive Diagnostic Engine — Frontend Integration

**Input**: Design documents from `/specs/006-adaptive-diagnostic-engine/`
**Prerequisites**: spec.md
**Organization**: 2 phases — Component fixes then integration

## Phase 1: Fix Design Tokens (Foundation)

- [x] T001 Fix Tailwind tokens in DiagnosticRunner.vue: replace warm- → ink-, primary- → teal-, bg-white → bg-surface, text-white → text-on-primary, bg-surface-bright → bg-surface-container, etc. in `frontend/src/components/student/DiagnosticRunner.vue`
- [x] T002 Fix Tailwind tokens in PassportAssessment.vue: same token replacements in `frontend/src/components/student/PassportAssessment.vue`
- [x] T003 Fix Tailwind tokens in KnowledgeAtom.vue: same token replacements in `frontend/src/components/student/KnowledgeAtom.vue`
- [x] T004 Fix Tailwind tokens in CompetencyHeatmap.vue: replace warm- → ink-, primary- → teal-, etc. in `frontend/src/components/expert/CompetencyHeatmap.vue` (per standing fix pattern)

## Phase 2: Integration & Features

- [x] T005 Integrate DiagnosticRunner into DiagnosticSession.vue: replace stub with full DiagnosticRunner component, pass moduleId from route params in `frontend/src/views/student/DiagnosticSession.vue`
- [x] T006 Add error classification feedback display in DiagnosticRunner: show Arabic message after incorrect answers (RESOURCE/PROCESS/INCIDENTAL) in `frontend/src/components/student/DiagnosticRunner.vue`
- [x] T007 Add group placement (A/B/C) display in results screen with Arabic descriptions in `frontend/src/components/student/DiagnosticRunner.vue`
- [x] T008 Add feedback animation/transition after answer submission in `frontend/src/components/student/DiagnosticRunner.vue`

## Phase 3: Verification

- [x] T009 Build check — verify no ESLint errors, no banned Tailwind classes
- [x] T010 Verify DiagnosticSession renders DiagnosticRunner with proper route params
