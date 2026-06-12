# Feature Specification: Remediation Pathways (Parcours de Remédiation)

**Feature Branch**: `007-remediation-pathways`
**Created**: 2026-06-13
**Status**: Draft
**Input**: Build the student-facing remediation session UI. The backend remediation engine (DynamicDifficultyAdjuster, StudentEngagementTracker, PathwayGenerator, PassportEvaluator, RemediationEngine) and API endpoints are fully implemented. This spec covers the frontend Vue 3 components, views, and service integration needed to deliver the complete remediation experience.

---

## Summary

Students who complete a diagnostic assessment are placed into remediation groups (A, B, or C) per competency. The remediation pathway delivers targeted **knowledge atoms** (micro-learning activities) with conditional progression — a student cannot advance until the current atom is completed. Atoms are presented in three modalities (audio-visual, virtual simulation, mind map) based on difficulty type. As the student interacts, the backend dynamically adjusts difficulty based on response speed and accuracy. Once sufficient atoms are completed, the student unlocks a **Passport assessment** that verifies mastery before advancing or triggers pedagogical alerts on failure.

The frontend must implement the full remediation session flow: pathway overview → atom-by-atom progression with difficulty feedback → Passport assessment → result display with badge awarding or retry path.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Student Receives Remediation Pathway After Diagnostic (Priority: P1)

A student who completed the Mathematics diagnostic for "fraction subtraction" and was placed in Group B opens their dashboard, selects the remediation card for that competency, and is presented with a personalized pathway overview showing all knowledge atoms in sequence. The UI indicates which atoms are locked (prerequisites not met), which are available, and which are completed. A progress bar shows overall pathway completion.

**Why this priority**: This is the entry point — without a clear pathway view, the student cannot begin remediation.

**Independent Test**: Log in as a student with a completed diagnostic, navigate to a competency with a generated pathway, and verify the pathway overview displays atoms in correct order with proper locked/available/completed states.

**Acceptance Scenarios**:

1. **Given** a student with a diagnostic result for "addition-fractions", **When** they navigate to the remediation session for that competency, **Then** the pathway is fetched from `GET /remediation/pathway/{competency_id}` and all atoms are displayed with type icons (🎬 audio-visual, 🎮 simulation, 🧠 mind map).
2. **Given** a pathway with 6 atoms where 2 are completed, **When** the overview renders, **Then** completed atoms show ✓, the next available atom is highlighted, and remaining atoms show a lock icon with tooltip "Complete previous activities first."
3. **Given** a pathway that has not been started, **When** the overview loads, **Then** only the first atom is available; all others are locked.
4. **Given** a pathway where all atoms are completed but the Passport has not been taken, **When** the overview renders, **Then** a prominent "Take Passport Assessment" call-to-action is displayed.
5. **Given** the pathway overview, **When** the student clicks an available atom, **Then** the UI transitions to the atom interaction view; **When** they click a locked atom, **Then** nothing happens and a gentle tooltip explains why.

---

### User Story 2 — Student Completes Knowledge Atoms with Adaptive Difficulty (Priority: P1)

A student opens the first knowledge atom — an audio-visual story about fraction subtraction. After watching the media, they complete an interactive drag-and-drop exercise. The frontend tracks interaction count and time spent, then sends completion data to `POST /remediation/atoms/{atom_id}/complete`. The backend returns a new difficulty level, progress percentage, and engagement recommendation (e.g., "Great job! Let's try something more challenging" or "Take a break and try a simpler exercise"). The UI displays the recommendation and adjusts the difficulty meter accordingly. The next atom is automatically loaded if available.

**Why this priority**: Atom interaction is the core remediation experience. The adaptive feedback loop (difficulty meter + engagement messages) is what differentiates Ihsane from static drill platforms.

**Independent Test**: Open any knowledge atom, interact with its content, mark it complete via the API, verify the difficulty meter updates and engagement recommendation displays.

**Acceptance Scenarios**:

1. **Given** an audio-visual atom with a media URL, **When** the atom view loads, **Then** the media player renders in an `aspect-video` container with play/pause controls and captions in the student's language (Arabic/French).
2. **Given** a simulation atom with interactive blocks, **When** the student drags or taps interactive elements, **Then** each interaction increments the interaction counter and the UI provides immediate visual feedback (highlight, shake on error, celebration on success).
3. **Given** a mind map atom, **When** the view renders, **Then** concepts are displayed as connected nodes with animated connections appearing as the student explores, showing the relationship between main concept, sub-concepts, and related ideas.
4. **Given** a student who completes an atom with 85% accuracy in 12 seconds, **When** completion is submitted, **Then** the difficulty meter rises from 5 → 6 or 7 and the recommendation reads "Great job! Let's try something more challenging."
5. **Given** a student who completes an atom slowly with incorrect answers, **When** completion is submitted, **Then** the difficulty meter drops and the recommendation is empathetic ("Take your time — you're doing great!").
6. **Given** an atom marked complete, **When** the next atom exists, **Then** the UI automatically transitions to the next atom after a 2-second delay showing a checkmark animation.
7. **Given** the last atom has been completed but the Passport threshold (50% progress or 3+ atoms) has not been met, **When** the student returns to the overview, **Then** the "Take Passport Assessment" button remains disabled with an explanatory message.

---

### User Story 3 — Passport Assessment Validates Mastery (Priority: P1)

After completing enough knowledge atoms, the student takes the Passport assessment: 5 questions that verify competency mastery. Questions are fetched from `GET /remediation/passport/questions/{competency_id}`. The student answers each question; the UI shows progress (question 3 of 5). After the last question, answers are submitted to `POST /remediation/passport/evaluate`. On success, the UI celebrates with a badge animation and shows the new mastery level (e.g., Familiar → Proficient). On failure, the UI displays an encouraging message, the option to retry, and optionally returns to the pathway overview for more practice.

**Why this priority**: The Passport is the gate — it validates that remediation was effective and controls advancement. Without it, there's no way to measure or enforce mastery.

**Independent Test**: Reach the Passport threshold for a competency, answer all 5 questions, submit, and verify the results screen correctly displays pass/fail, accuracy, mastery level change, badge awarding, and retry flow.

**Acceptance Scenarios**:

1. **Given** a student who has met the Passport threshold (≥50% progress or ≥3 atoms completed), **When** they click "Take Passport Assessment", **Then** 5 questions load with a progress bar showing "Question 1 of 5".
2. **Given** a Passport question of type `multiple_choice`, **When** the student selects an option, **Then** the selection is highlighted with a visual indicator (filled radio circle); **When** they click "Next" or "Submit", **Then** the answer is recorded with response time.
3. **Given** a Passport question of type `text` or `interactive`, **When** the student inputs their answer, **Then** the input is validated (non-empty) before allowing submission.
4. **Given** all 5 questions answered, **When** the submit call returns with `passed: true` and `accuracy: 0.85`, **Then** the results screen shows:
   - 🏆 trophy icon with "Congratulations!" heading
   - Accuracy: 85%, Correct: 4/5
   - Previous level → New level (e.g., Familiar → Proficient)
   - ⭐ Badge earned notification with animated entrance
   - "Finish" button navigating back to dashboard.
5. **Given** the submit call returns with `passed: false` and `alert_triggered: true`, **Then** the results screen shows:
   - 💪 encouragement icon with "Keep practicing!" heading
   - Accuracy display and mastery level (unchanged or regressed)
   - Alert banner noting that parents/experts have been notified
   - "Retry" button that reloads fresh questions
   - "Return to Pathway" button to continue practicing.
6. **Given** a student who passes the Passport, **When** they return to their dashboard, **Then** the competency card reflects the new mastery level and the competency badge is visible in their collection.

---

### Edge Cases

- **What happens when the pathway API returns zero atoms?** → The UI displays an empty state with the message "No remediation activities are available for this skill yet. Your teacher has been notified." and a button to return to the dashboard.
- **What happens when a student navigates away mid-atom?** → Interaction count and time are not persisted locally for the stub; the atom must be re-completed. In production, IndexedDB (Dexie.js) will cache partial state for offline resume.
- **What happens when the complete-atom API call fails (network error)?** → The UI retries once automatically. On second failure, it displays an error toast: "Could not save your progress. Please check your connection and try again." with a manual retry button.
- **What happens when a student's engagement triggers a frustration alert?** → The recommendation response is displayed prominently above the next atom: a calming message with a suggested pause. The UI offers a "Take a short break" button that shows a gentle 30-second timer with animated breathing guide.
- **What happens when a Passport assessment loads zero questions?** → The UI displays "Assessment questions are being prepared. Please try again in a moment." with a retry button. The student can return to the pathway overview in the meantime.
- **What happens when the student rapidly clicks submit multiple times?** → The submit button is disabled immediately on first click and shows a spinner; duplicate submissions are prevented.
- **What happens when a student is in the middle of a Passport assessment and the session expires?** → The router guard detects the 401 response, preserves the current question index in session storage, and redirects to login. After re-authentication, the student is returned to the saved question index.
- **What happens during RTL (Arabic) mode?** → All layout, progress bars, navigation arrows, and interaction directions mirror correctly. Media controls, difficulty meters, and atom type icons flow right-to-left.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Pathway View & Navigation

- **FR-001**: The `RemediationSession` view MUST fetch the remediation pathway from `GET /remediation/pathway/{competencyId}?student_group={group}` on mount and display a pathway overview with all knowledge atoms in sequence.
- **FR-002**: The pathway overview MUST render each atom with its remediation type icon (🎬 AUDIO_VISUAL, 🎮 SIMULATION, 🧠 MIND_MAP), title, description, and status indicator (locked 🔒, available ▶, completed ✓).
- **FR-003**: Progression MUST be strictly conditional: only the first uncompleted atom is clickable; all subsequent atoms are locked and visually disabled until the current one is completed.
- **FR-004**: A global pathway progress bar MUST be displayed showing `progress_percent` with the fraction `atoms_completed / total_atoms`. The bar MUST animate smoothly on progress updates.

#### Atom Interaction & Adaptive Feedback

- **FR-005**: The `KnowledgeAtom` component MUST render atom content based on `remediation_type`:
  - **AUDIO_VISUAL**: Media player for `content.media_url` with Arabic/French captions, plus the interactive exercise area.
  - **SIMULATION**: Draggable/tappable interactive blocks with visual feedback (highlight on hover, snap on correct placement, shake on incorrect).
  - **MIND_MAP**: Connected concept nodes rendered as an expandable tree or cluster, with animated connections appearing progressively.
- **FR-006**: The atom completion flow MUST:
  1. Track `interaction_count` (incremented on each tap/drag/click in interactive areas).
  2. Track elapsed `time_spent_ms` from atom open to completion.
  3. Call `POST /remediation/atoms/{atomId}/complete` with `{ time_spent_ms, interactions_count, is_correct }`.
  4. Display the response data: updated `progress_percent`, `new_difficulty`, `recommendation` message, and `next_atom` if available.
- **FR-007**: A `DifficultyMeter` component MUST display the current difficulty level (1–10) as a segmented bar. After each atom completion, it MUST animate from the old difficulty to the new value, with color coding (green 1–3, amber 4–7, red 8–10).
- **FR-008**: Engagement recommendations from the backend (`recommendation` field) MUST be displayed as a dismissible banner with contextual styling:
  - Frustration recommendation: amber background, 💆 breather icon, "Take a break" action button.
  - Boredom recommendation: green background, 🚀 rocket icon, encouragement text.
  - Neutral: no banner shown.

#### Passport Assessment

- **FR-009**: The `PassportAssessment` component MUST fetch questions from `GET /remediation/passport/questions/{competencyId}` and render one question at a time with a progress indicator ("Question X of Y").
- **FR-010**: The component MUST support at minimum two question types based on `content.type`:
  - `multiple_choice`: Rendered as tappable option buttons (minimum 60px touch targets) with selected-state highlight.
  - `text`: Rendered as an input field with Arabic/French keyboard support.
- **FR-011**: Each answer submission MUST record `question_id`, `answer` string, and `time_ms` (milliseconds since question was displayed). On the final question (index === questions.length - 1), all answers MUST be submitted as a batch to `POST /remediation/passport/evaluate`.
- **FR-012**: The Passport results screen MUST display:
  - Pass/fail state with appropriate iconography (🏆 pass, 💪 fail).
  - Accuracy percentage, correct count / total.
  - Previous mastery level → New mastery level transition with direction arrow and color change (green for advancement, amber for regression).
  - Badge earned (⭐ with competency name) on pass, with CSS entrance animation.
  - Alert banner when `alert_triggered: true`, informing the student that their teacher has been notified.
  - "Retry" button (on fail) that reloads fresh questions from the API.
  - "Finish" / "Return to Dashboard" button.

#### Integration & Routing

- **FR-013**: The `RemediationSession` view MUST be accessible at route `/student/remediation/:competencyId`. The `competencyId` route param MUST drive all API calls.
- **FR-014**: The existing `remediationService.ts` frontend service MUST be used for all API communication. No new HTTP logic bypassing this service is permitted.
- **FR-015**: All user-facing text MUST be defined in the i18n locale files (`ar.json` and `fr.json`) under a `remediation` namespace, with keys for: pathway title, atom type labels, completion messages, Passport labels, difficulty labels, engagement messages, empty states, and error messages.

#### Accessibility & RTL

- **FR-016**: All interactive elements (atom cards, question options, buttons) MUST have minimum 60px touch targets.
- **FR-017**: All layouts MUST use CSS logical properties (`inline-start`/`inline-end` instead of `left`/`right`) to ensure correct RTL mirroring in Arabic mode.

### Key Entities (Frontend View)

- **RemediationPath**: The orchestrating view state — holds the fetched pathway (id, atoms list, atoms_completed list, progress_percent, current_difficulty, status). Manages which atom is currently active and whether the Passport is unlocked.
- **KnowledgeAtom (view model)**: Renders a single micro-learning activity. Has type (AUDIO_VISUAL, SIMULATION, MIND_MAP), content (title, description, media_url, interactive_data), completion state, and order in pathway.
- **PassportAssessment (view model)**: Manages the assessment flow — questions array, current index, answers map, loading/submitting/result states.
- **DifficultyMeter**: A presentational component receiving `currentDifficulty` (1–10) as a prop, rendering a segmented bar with animated transitions.
- **PathwayProgressBar**: A presentational component receiving `percent` and `completed/total` counts, rendering an animated progress bar with fraction text.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A student can navigate from dashboard → remediation session → first atom in under 2 seconds (pathway API response < 200ms, component render < 500ms).
- **SC-002**: Atom completion submission receives an API response and updates the UI (difficulty meter, progress bar, recommendation banner) within 500ms of the submit call returning.
- **SC-003**: Passport assessment flow (load questions → answer 5 → submit → view results) completes end-to-end without console errors or UI freezes.
- **SC-004**: The difficulty meter animates smoothly (CSS transition, no layout shift) when updating between difficulty levels.
- **SC-005**: All interactive elements pass the 60px minimum touch target requirement when measured in the rendered DOM.
- **SC-006**: The remediation session renders correctly in both Arabic (RTL) and French (LTR) modes with no broken layouts, mirrored navigation, or text clipping.
- **SC-007**: The empty state (zero atoms returned) is handled gracefully without a white screen or uncaught error.
- **SC-008**: The retry flow on Passport failure reloads fresh questions from the API (different `assessment_id`) and the student can complete a second attempt.

---

## Assumptions

- The backend remediation engine and all five API endpoints (`GET /pathway`, `POST /atoms/{id}/complete`, `GET /status`, `GET /passport/questions`, `POST /passport/evaluate`) are implemented, tested, and conform to the schemas defined in `backend/app/schemas/remediation.py`.
- The frontend service `remediationService.ts` accurately types all request/response shapes and the API base URL is correctly configured.
- The diagnostic session flow already routes students to the remediation session with the correct `competencyId` and `studentGroup` parameters.
- Vue 3 Composition API (`<script setup>`), TypeScript, vue-i18n, and Tailwind CSS (utility classes: `bg-warm-*`, `text-primary-*`, `rounded-2xl`, `shadow-soft`) are the established frontend conventions.
- Existing stub components (`RemediationSession.vue`, `KnowledgeAtom.vue`, `PassportAssessment.vue`) serve as starting points and will be substantially enhanced.
- The competency profile (BKT state, mastery level) is maintained server-side; the frontend only displays and acts on the data returned by API responses.
- Offline caching of remediation atom content via Dexie.js/Workbox is deferred to a future feature and is not in scope for this spec.
