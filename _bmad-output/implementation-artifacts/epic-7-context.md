# Epic 7 Context: Pre-Literate Student Accessibility

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Pre-literate Year 1-2 students can take diagnostics via audio read-aloud (question text spoken aloud in the item's language) and image-choice answer options (tapping pictures instead of reading text). The full author→render→score pipeline supports multiple_choice, image_choice, and numeric item types.

## Stories

- Story 7.1: Audio Read-Aloud for Question Text (FR-8b)
- Story 7.2: Image-Choice Item Type (FR-8c)

## Requirements & Constraints

- FR-8b: Audio read-aloud of question text for Y1-2 pre-literate students (AR/FR support).
- FR-8c: Image-choice item type where options are image URLs instead of text.
- Full author -> render -> score pipeline must support multiple_choice, image_choice, and numeric item types.

## Technical Decisions

- Frontend: Vue 3 + TypeScript + Tailwind CSS.
- Component `DiagnosticQuestion.vue` handles rendering options based on item type (`multiple_choice`, `image_choice`, `numeric`).
- Component `QuestionEditor.vue` handles authoring of item types.
- Backend: FastAPI + SQLAlchemy. Question model supports `type: "image_choice"` with options containing image URLs.
- Answer scoring backend logic evaluates selected image choice option against correct answer key.
