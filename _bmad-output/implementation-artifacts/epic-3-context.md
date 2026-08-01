# Epic 3 Context: Remediation Lifecycle, AI Pipeline & Mastery Loop

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Students receive AI-generated remediation pathways. The pathway generation combines deterministic selection of knowledge atoms with LLM augmentation. Pedagogues must validate these proposals before students can see or start them. A strict state machine governs the full lifecycle transitions. Failed questions are re-introduced at spaced intervals. To verify mastery, the student must pass a single competency-scoped Passport task, which awards a badge or triggers alerts.

## Stories

- Story 3.1: Remediation State Machine, Add Missing States and Transition Guard
- Story 3.2: Celery Tasks Infrastructure and LiteLLM Integration
- Story 3.3: Expert Validation Queue and Workflow
- Story 3.4: Student Remediation Execution, Atom Delivery and Progress Tracking
- Story 3.5: Spaced Re-Surfacing of Failed Items
- Story 3.6: Passport Competency Task, Wire Orphaned Component
- Story 3.7: Frontend remediationStore and Remediation Session Views

## Requirements & Constraints

- Generate a remediation pathway (FR-14): Gaps identified by the diagnostic engine yield a pathway sequencing specific knowledge atoms. Each pathway must enter the proposed state for expert review before student access.
- Concrete to abstract atom delivery (FR-15): Content must progress from sensory, interactive, or audio-visual resources to abstract symbolic concepts.
- Spaced re-surfacing (FR-16): Previously failed items must be re-introduced at spaced intervals rather than immediately re-drilled.
- Mastery tracking (FR-17): The system maintains a four-level competency profile (Attempted, Familiar, Proficient, Mastered) updated by BKT and Passport outcomes.
- Passport task (FR-18): Students attempt a single competency-scoped task to verify mastery after finishing pathway atoms.
- Badge and alert logic (FR-19): Passing the Passport awards a badge and unlocks the next competency. Failing raises a warning alert and suggests a physical support plan.
- State machine transitions (AD-2): The service layer enforces all transitions. API controllers cannot modify status directly.
- Hybrid AI generation (AD-3): The generation pipeline runs asynchronously through Celery and LiteLLM. A deterministic baseline is created first, then augmented by the LLM. If the LLM fails, the deterministic pathway remains valid.
- Multi-tenant proposal routing (AD-4): School proposals route to the school's experts. Household proposals route to the platform pedagogue pool.
- Web safety: No child personal identifiable information can be logged or sent to external LLMs.

## Technical Decisions

- Core Data Models:
  - `RemediationPath` status field is governed by a strict state machine: DIAGNOSED, PROPOSED, VALIDATED, IN_PROGRESS, COMPLETED, PASSPORT_TESTING, MASTERED.
  - State machine transitions:
    - DIAGNOSED -> PROPOSED (triggered by async AI generation task)
    - PROPOSED -> VALIDATED (approved by expert)
    - PROPOSED -> DIAGNOSED (rejected by expert, triggers regeneration with feedback)
    - VALIDATED -> IN_PROGRESS (student starts remediation)
    - IN_PROGRESS -> COMPLETED (student completes all atoms)
    - IN_PROGRESS -> ABANDONED (student, expert, or timeout trigger)
    - COMPLETED -> PASSPORT_TESTING (student launches Passport task)
    - PASSPORT_TESTING -> MASTERED (student passes Passport task, updates mastery profile)
    - PASSPORT_TESTING -> DIAGNOSED (student fails Passport task, raises alert)
    - ABANDONED -> PROPOSED (expert adjusts, triggers regeneration)
    - ABANDONED -> RETIRED (expert retires path)
  - `SpacedRepetition` model tracks `question_id`, `student_id`, `next_review_date`, `interval_days`, and `ease_factor`.
- Hybrid AI Pipeline:
  - The API router enqueues an asynchronous Celery task upon diagnostic completion.
  - Celery workers use the LiteLLM client to interact with external language models.
  - Backend configurations define the default model via `LLM_MODEL` settings.
- Routing Rule:
  - Queries for the expert queue check the organization type.
  - School organization proposals route to the respective school's experts.
  - Household organization proposals route to experts with the platform pedagogue flag.
- Passport Verification:
  - The assessment uses a single competency-scoped task.
  - This assessment is not a cumulative exam and evaluates only the target competency.

## UX & Interaction Patterns

- Expert validation dashboard:
  - Experts view a list of proposed pathways showing the student name, failed competency, AI justification, and selected atoms.
  - Controls allow the expert to validate or reject the proposal with text feedback.
- Student remediation interface:
  - Vue components display atoms sequentially based on the concrete to abstract order.
  - Students cannot skip atoms or access the Passport task prematurely.
- Passport task presentation:
  - The UI displays the assessment task in a distraction-free view once the pathway is completed.
- Language support:
  - Layout direction flips instantly between Arabic and French using logical CSS properties.

## Cross-Story Dependencies

- Frontend session views (Story 3.7) depend on the Axios camelCase transformer implemented in Epic 1 (Story 1.1).
- The expert validation queue (Story 3.3) depends on the Celery and LiteLLM infrastructure (Story 3.2).
- Student execution (Story 3.4) requires the state machine backend endpoints (Story 3.1).
- All stories in this epic depend on the multi-tenancy context (Epic 1) and the stateless engine layout (Epic 2).
