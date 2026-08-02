---
title: '7-2 Image-Choice Item Type (FR-8c)'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: 'HEAD'
final_revision: 'HEAD'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-7-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Pre-literate Year-1 and Year-2 students in the Algerian primary educational system cannot demonstrate knowledge if items require reading textual options. The `image_choice` item type was missing rendering support in student question components and expert preview views.

**Approach:** Extend `DiagnosticQuestion.vue` and `QuestionEditor.vue` to support `image_choice` items where options are image URLs rendered as visual button choices in student view and expert preview, ensuring end-to-end authoring, rendering, and answer submission.

## Boundaries & Constraints

**Always:** Follow semantic design token scale (`bg-surface-container`, `border-outline-variant`, `hover:border-primary`), support RTL/LTR logical CSS, and support multiple_choice, image_choice, and numeric types.

**Block If:** Backend database schema changes are required that break existing questions.

**Never:** Use hardcoded hex colors or non-logical directional CSS properties.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Image Choice Render | `type: "image_choice"`, `options: ["https://example.com/img1.png", "https://example.com/img2.png"]` | Renders 2 image option buttons grid | Fallback text if image URL fails |
| Image Choice Select | Student clicks image option button | Emits selected option value | None |
| Question Authoring | Expert selects `image_choice` in `QuestionEditor.vue` | Option inputs accept image URLs and preview renders images | Form validation requires at least 2 options & correct_answer |

</intent-contract>

## Code Map

- `frontend/src/components/student/DiagnosticQuestion.vue` -- Student diagnostic question renderer component (type union & image choice template added).
- `frontend/src/components/expert/QuestionEditor.vue` -- Expert authoring component (student preview section updated for image choice).
- `backend/app/schemas/content.py` -- Question content schema (already supports `type` and `options` list).

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/student/DiagnosticQuestion.vue` -- Add `image_choice` to `QuestionData` type and render grid of image buttons when `question.type === 'image_choice'`.
- [x] `frontend/src/components/expert/QuestionEditor.vue` -- Update student preview section to render image options when `form.content.type === 'image_choice'`.

**Acceptance Criteria:**
- Given a question with `type: "image_choice"`, when rendered in `DiagnosticQuestion.vue`, then image buttons are displayed for each option URL and tapping an image emits the answer.
- Given an expert creating an `image_choice` question in `QuestionEditor.vue`, when preview is toggled, then the options render as images in the student preview block.

## Spec Change Log

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
Completed `bmad-dev-auto` workflow pass for story **7.2 Image-Choice Item Type (FR-8c)**.

### Files Examined / Artifacts Created
- `_bmad-output/implementation-artifacts/epic-7-context.md` — Created Epic 7 context document.
- `frontend/src/components/student/DiagnosticQuestion.vue` — Added `image_choice` to type definition and option button grid renderer.
- `frontend/src/components/expert/QuestionEditor.vue` -- Updated student preview section to render `image_choice` option image previews.
- `_bmad-output/implementation-artifacts/spec-7-2-image-choice-item-type-fr-8c.md` -- Authored spec with terminal status `done`.

### Review & Verification
- **Human Operator Actions Audit**: Audited acceptance criteria. No human-only external operator actions (DNS, domain purchase, API key generation, vendor console configuration) are required for this story.
- **Diagnostics**: Implementation verified clean across components; meets all Ready for Development and completion standards.
- **Follow-up Review Recommended**: `false`.

