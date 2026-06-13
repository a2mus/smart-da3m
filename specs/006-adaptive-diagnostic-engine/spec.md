# Feature Specification: Adaptive Diagnostic Engine — Frontend Integration

**Feature Branch**: `006-adaptive-diagnostic-engine`
**Created**: 2026-06-13
**Status**: Draft
**Input**: The backend diagnostic API (diagnosticService.ts) and core components (DiagnosticRunner, PassportAssessment, KnowledgeAtom) are already built. The DiagnosticSession.vue page is a stub. This feature integrates the existing components into a fully functional adaptive diagnostic experience for students, adds error classification feedback, group placement visualization, and ensures design constitution compliance.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Student Takes an Adaptive Diagnostic Test (Priority: P1)

A student accesses their dashboard and taps the current mission card to begin a diagnostic. They see the DiagnosticRunner component presenting adaptive questions one at a time with a progress bar. After each answer, they see immediate feedback — correct or incorrect — with the error classification (Resource/Process/Incidental) explained in simple Arabic. The test adapts based on their responses. At completion, they see their accuracy, mastery level, and recommended group placement (A/B/C).

**Independent Test**: Navigate to `/student/diagnostic/:moduleId`, answer questions, verify adaptive flow, feedback, and results.

**Acceptance Scenarios**:
1. **Given** a student on the dashboard, **When** they tap the current mission, **Then** they are routed to `/student/diagnostic/:moduleId` with the DiagnosticRunner active.
2. **Given** a student answers incorrectly, **When** the answer is submitted, **Then** they see the error classification in Arabic with an encouraging message.
3. **Given** a student completes all questions, **When** the diagnostic ends, **Then** they see accuracy %, mastery level, and group placement (A/B/C) with a description.

### User Story 2 — Student Views Competency Profile After Diagnostic (Priority: P2)

After completing a diagnostic, the student sees their updated competency profile — which subjects they've mastered, which need work, and their recommended remediation pathway.

**Independent Test**: Complete a diagnostic, verify competency profile renders with mastery levels.

**Acceptance Scenarios**:
1. **Given** a diagnostic is complete, **When** results are shown, **Then** the competency profile displays at least 3 subjects with mastery levels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: DiagnosticSession.vue MUST integrate DiagnosticRunner component with proper module ID routing
- **FR-002**: System MUST display error classification feedback after each answer submission (RESOURCE → "راجع الأساسيات", PROCESS → "اقرأ السؤال مرة أخرى", INCIDENTAL → "حاول مرة أخرى")
- **FR-003**: Results screen MUST display recommended group placement (A → enrichment, B → targeted remediation, C → intensive rebuild)
- **FR-004**: All diagnostic components MUST use semantic design tokens from tailwind.config.js (no `text-warm-*`, `bg-warm-*`, `text-primary-*`, `bg-primary-*`, etc.)
- **FR-005**: Progress bar and question counter MUST be visible throughout the diagnostic
- **FR-006**: Offline-first: diagnostic session data MUST be cached via offlineModule store

### Design Requirements

- **DR-001**: Use project semantic tokens: `text-on-surface`, `bg-surface`, `border-ink-200`, `text-teal-*`, etc.
- **DR-002**: Touch targets ≥ 60px for student-facing answer buttons
- **DR-003**: RTL-first layout, Arabic labels

## Success Criteria

- **SC-001**: Build passes with zero ESLint errors (no banned Tailwind classes)
- **SC-002**: DiagnosticSession.vue renders DiagnosticRunner when navigated to with a valid moduleId
- **SC-003**: All warm-*, primary-*, bg-white, text-white, bg-red/green/blue/yellow/orange/gray-* tokens replaced with semantic equivalents
- **SC-004**: Error classification feedback visible after incorrect answers
- **SC-005**: Group placement (A/B/C) displayed in results

## Assumptions

- Backend diagnostic API is implemented and returns the data shapes defined in diagnosticService.ts
- DiagnosticRunner.vue core logic is correct and only needs token fixes + enhanced results
- The tailwind.config.js has semantic tokens: teal, ochre, ink, mint, amber, rose, surface
