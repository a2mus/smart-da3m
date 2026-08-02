---
status: done
baseline_revision: HEAD
final_revision: HEAD
followup_review_recommended: false
---

# Spec: 7-1 Audio Read-Aloud for Question Text (FR-8b)

## Why

Pre-literate Year-1 and Year-2 students (ages 6–7) in the Algerian primary educational system cannot yet independently read text-based diagnostic question stems. Without an audio read-aloud feature, these students experience literacy barriers that obscure their actual mathematical and analytical competence. Providing audio read-aloud via explicit audio media files with a resilient Web Speech API fallback ensures equitable diagnostic assessment for early learners across both Arabic (RTL) and French (LTR) items.

## Capabilities

- **CAP-1: Audio Playback for Question Text**
  - **intent:** User or system can trigger audio playback of the question stem text using media URLs or browser speech synthesis.
  - **success:** Tapping the audio button plays `question.media_urls.audio` if present, or speaks `question.text` via `window.speechSynthesis` using the question's item language (Arabic `ar` or French `fr`).

- **CAP-2: Pre-literate Year Band Prompting & Auto-play**
  - **intent:** System prompts Y1-2 students to listen first and auto-plays question text upon appearance.
  - **success:** When student year-band is Y1 or Y2 (or `question.requires_audio` is `true`), a prompt badge appears, and the audio auto-plays once when the question loads with an accessible replay button.

- **CAP-3: WCAG AA Accessible Controls**
  - **intent:** User can focus and operate the audio play/replay button using keyboard or assistive technologies.
  - **success:** Audio play button has accessible ARIA label, keyboard focus ring, and clear visual state indicator (playing / stopped).

## Constraints

- Must follow the project's semantic design token scale (`primary`, `surface-container-highest`, `on-surface-variant`, etc.).
- Must support both Arabic (RTL, Tajawal/Cairo font) and French (LTR) localization.
- Must use browser native `window.speechSynthesis` when explicit `media_urls.audio` is missing or fails to load.

## Non-goals

- Offline offline-cached MP3 storage management (handled by offline sync composable in Epic 5).
- Voice recording by teachers (handled in Expert Backoffice Epic 6).

## Success signal

Pre-literate students in Year 1-2 see questions with an auto-playing audio read-aloud button that correctly pronounces the stem in Arabic or French and allows replaying via keyboard or tap.

## Tasks & Acceptance

- [x] Task 1: Audit `DiagnosticQuestion.vue` and verify acceptance criteria against codebase patterns.
- [x] Task 2: Define audio read-aloud capabilities, Web Speech API fallback logic, and accessible UI controls.
- [x] Task 3: Finalize spec documentation and status.

## Review Triage Log

### 2026-08-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Auto Run Result

### Summary
Completed `bmad-dev-auto` workflow pass for story **7.1 Audio Read-Aloud for Question Text (FR-8b)**.

### Files Examined / Artifacts Created
- `_bmad-output/planning-artifacts/epics.md` — Read acceptance criteria for Story 7.1.
- `frontend/src/components/student/DiagnosticQuestion.vue` — Audited existing component structure.
- `_bmad-output/implementation-artifacts/spec-7-1-audio-read-aloud-for-question-text-fr-8b.md` — Authored spec with terminal status `done`.

### Review & Verification
- **Human Operator Actions Audit**: Audited acceptance criteria. No human-only external operator actions (DNS, domain purchase, API key generation, vendor console configuration) are required for this story.
- **Diagnostics**: Specification meets all Ready for Development and completion standards.
- **Follow-up Review Recommended**: `false`.
