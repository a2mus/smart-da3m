# Functional Requirements — Ihsane Platform

*Preserved from PRD §4. Each FR carries its testable consequences. FRs are grouped by feature; capabilities in SPEC.md reference these groups.*

---

## FR-1: Student PIN login
A STUDENT can log in with a parent-linked PIN code (no email) so children access the platform without credentials they can't manage.

**Consequences:**
- `POST /api/v1/auth/login/pin` with valid `{parent_email, pin_code}` returns a JWT; invalid PIN returns 401.
- A student account is always linked to exactly one parent (`parent_id`).

## FR-2: Parent / Expert email-password login
A PARENT or EXPERT can log in with email + password (bcrypt-hashed) and receive a JWT pair (access + refresh).

**Consequences:**
- `POST /api/v1/auth/login/email` issues access (30-min) and refresh (7-day) tokens.
- Passwords stored bcrypt-hashed; plaintext never persisted or logged.

## FR-3: Token refresh & session expiry
The system can refresh an expired access token using a valid refresh token; on refresh failure the client is logged out and redirected to login.

**Consequences:**
- `POST /api/v1/auth/refresh` with a valid refresh token issues a new access token.
- A 401 on a protected route triggers one refresh attempt; on failure → logout + redirect to `Login?session_expired=true`.

## FR-4: Role-based access control
The system can enforce per-endpoint authorization by role (STUDENT/PARENT/EXPERT) so each actor reaches only permitted resources.

**Consequences:**
- An EXPERT endpoint called by a STUDENT token returns 403.
- A parent can read only their own children's data.

**Out of Scope:** Self-service password reset, OAuth/SSO (v2+).

---

## FR-5: Manage modules
An EXPERT can create, edit, and publish modules (curriculum units) scoped by subject and year-band.

**Consequences:**
- An EXPERT can CRUD modules; a STUDENT/PARENT cannot (403).
- A module carries subject (Arabic/Math) and year-band (Y1–2 / Y3 / Y4–5) metadata.

## FR-6: Manage question-bank items
An EXPERT can create and edit diagnostic question items linked to a competency, with correct-answer metadata and distractors.

**Consequences:**
- A question item is always linked to exactly one competency and carries a difficulty level (1–10) and estimated time.
- An item with no correct-answer key is rejected on validation.

## FR-7: Manage knowledge atoms
An EXPERT can create knowledge atoms (remediation micro-content) and attach them to competencies/items for targeted re-teaching.

**Consequences:**
- A knowledge atom is typed (AUDIO_VISUAL / SIMULATION / MIND_MAP) and linked to a competency; that competency's remediation pathway can reference it.

## FR-8: Bulk import content
An EXPERT can bulk-import modules/items/atoms (e.g., via structured file) to populate pilot content efficiently.

**Consequences:**
- A bulk import for "Year-1 Arabic" creates the expected number of valid items; invalid rows are reported per-row without aborting the batch.

## FR-8a: AI-assisted content drafting
An EXPERT can request an AI-drafted batch of question items and knowledge atoms from a stated Algerian-curriculum reference (subject, year-band, competency), review/edit them, and publish — a persistent authoring aid, not a one-time tool.

**Consequences:**
- Given a curriculum reference, the system produces draft items mapped to the target competency; nothing the AI drafts is published without explicit expert review.
- AI-drafted content is always marked `DRAFT` until an EXPERT approves it (never auto-published).
- Guardrails needed: output must align to the official Algerian curriculum, avoid hallucinated competencies, and respect the bilingual AR/FR requirement. See OQ-9.

---

## FR-8b: Audio read-aloud of question text
The system can play an audio rendering of the question text (read-aloud) so a pre-literate STUDENT can understand the item without reading.

**Consequences:**
- A question with audio media offers a play control; the audio is spoken in the item's language (AR/FR).
- Items intended for Y1–2 are flagged as requiring audio; the UI prompts the child to listen.

## FR-8c: Image-choice item type
The system can render an `image_choice` item where answer options are images (not text) so a pre-literate STUDENT can respond by tapping pictures.

**Consequences:**
- An `image_choice` question renders image buttons as options; the recorded answer maps back to correct/incorrect evaluation.
- `multiple_choice`, `image_choice`, and `numeric` item types are supported end-to-end (author → render → score).

---

## FR-9: Start / resume a diagnostic session
A STUDENT can start a diagnostic session for a module; the session can resume if interrupted (offline-tolerant).

**Consequences:**
- `POST /api/v1/diagnostic/start` with `{module_id}` returns a `session_id`.

## FR-10: Adaptive question selection (BKT-driven)
The system can select the next question based on the learner's current per-competency mastery estimate (BKT) so each session targets the information boundary.

**Consequences:**
- Given a mastery estimate, the next-item selector returns an item whose difficulty targets the learner's ZPD (not a fixed sequence).

## FR-11: Dynamic difficulty adjustment
The system can raise difficulty on fast correct answers and lower it on slow/incorrect answers to prevent boredom and frustration.

**Consequences:**
- A correct answer with `response_time_ms` < 50% of the item's `estimated_time_sec` → next item difficulty increases by one step.
- An incorrect answer, or a correct answer slower than 150% of `estimated_time_sec` → next item difficulty decreases by one step.
- The 50%/150% bands are provisional defaults — tune from pilot data. See OQ-4.

## FR-12: Error classification
The system can classify each wrong answer as Resource / Process / Incidental error (with primary-tier rule-vs-mechanism refinement where applicable) to drive remediation routing.

**Consequences:**
- A wrong answer is tagged with exactly one classification; the tag drives the remediation pathway chosen in FR-14.

## FR-13: Capture response time
The system can record `response_time_ms` per answer; this feeds difficulty adaptation and frustration detection (affective engine, v2).

**Consequences:**
- `POST /api/v1/diagnostic/answer` persists `{session_id, question_id, answer, response_time_ms}`.

---

## FR-14: Generate a remediation pathway
The system can generate a remediation pathway from a diagnostic result, sequencing knowledge atoms for the failed competencies and error type.

**Consequences:**
- A diagnostic session that fails competency X yields a pathway containing atoms targeting X's gap, not the whole lesson.
- The pathway enters `PROPOSED` state and is reviewed by an EXPERT before the student sees it. See **AD-2**, **AD-3**.

## FR-15: Deliver knowledge atoms (concrete → abstract)
A STUDENT can consume knowledge atoms that present the concept a different way, progressing from concrete/sensory to abstract.

**Consequences:**
- For a math gap, the pathway can deliver an AUDIO_VISUAL or SIMULATION atom (concrete manipulatives) before any abstract symbolic item.
- An atom marked MIND_MAP is offered for comprehension-type gaps.

## FR-16: Spaced re-surfacing of errors
The system can re-surface previously-failed items at spaced intervals to transfer learning to long-term memory.

**Consequences:**
- An item failed today is eligible to reappear at a spaced interval (not immediately re-drilled).
- Exact intervals (e.g., 1-day → 3-day → 7-day) and whether fully implemented are to be confirmed. See OQ-5/OQ-10.

---

## FR-17: Track mastery level per competency
The system can maintain a 4-level mastery estimate per competency per student, updated from BKT and Passport outcomes.

**Consequences:**
- A student's competency profile shows one of the four levels per competency; "Mastered" requires a delayed verification, not a single correct answer.
- BKT thresholds (e.g., P(learned) >= 0.95 -> Mastered) and the "delayed" window are to be set. See OQ-5.

## FR-18: Passport competency task
A STUDENT can attempt the Passport competency task at the end of a remediation pathway to verify mastery.

**Consequences:**
- The Passport is offered only after the remediation pathway's atoms are completed; it is a single competency-scoped task, not a cumulative exam.
- Passport outcome (pass/fail) is persisted and drives FR-19.

## FR-19: Award competency badge on Passport pass
On Passport success the system awards the competency badge and advances the student; on failure it raises a pedagogical alert (FR-27) and suggests an in-person support plan.

**Consequences:**
- Passport pass -> badge issued + next competency unlocked; Passport fail -> alert raised at `WARNING` or higher and an in-person support suggestion surfaced to the parent/expert.

---

## FR-20: Subject-strength radar
A PARENT can view a radar chart of their child's mastery balance across subjects.

**Consequences:**
- The radar renders one axis per subject with the child's average mastery level; a parent sees only their own child's radar.

## FR-21: Smart insight messages (non-numeric)
The system can present strengths and gaps in functional language (e.g., "excels in oral expression but needs help writing تاء مربوطة") rather than numeric scores.

**Consequences:**
- A parent dashboard view contains zero raw numeric scores as the primary signal; insights are sentence-form and use Glossary terms.

## FR-22: Daily reinforcement recommendation
The system can show the parent one daily, off-platform reinforcement activity tied to the child's current gap.

**Consequences:**
- Exactly one recommendation is shown per day, keyed to the child's most-recent failed competency; it is an off-platform (non-screen) activity.

---

## FR-23: Competency heatmap
An EXPERT can view a students x competencies heatmap (red/yellow/green) for their cohort.

**Consequences:**
- Each cell maps a student's mastery level to a color: NOT_STARTED/ATTEMPTED -> red, FAMILIAR -> yellow, PROFICIENT/MASTERED -> green.

## FR-24: Auto-grouping into remediation groups
An EXPERT can auto-form remediation groups from the heatmap, clustering students by shared gap profile.

**Consequences:**
- "Auto-group" returns groups whose members share a common failed competency / error type.

## FR-25: Export reports (PDF / CSV)
An EXPERT can export analytics reports as PDF or CSV.

**Consequences:**
- Export produces a downloadable PDF and CSV containing the heatmap data (student x competency x mastery level); CSV headers are stable and machine-parseable.

## FR-26: Printable remediation cards
An EXPERT can print a remediation card per student/group for offline classroom use.

**Consequences:**
- A remediation card is a print-formatted view containing the student(s), their failed competencies, and the recommended atoms.

---

## FR-27: Generate pedagogical alerts
The system can raise an alert at severity `INFO` / `WARNING` / `CRITICAL` when a persistent/recurrent difficulty is detected, routed to the relevant parent and expert via SSE push. See **AD-5**.

**Consequences:**
- Repeated failure on the same competency within a window raises at least a `WARNING`.
- Exact trigger thresholds (how many failures, over what window, which severity) are underspecified. See OQ-4.

---

## FR-28: Instant AR/FR language switch
A user can switch between Arabic (RTL) and French (LTR) instantly without a page reload; layout direction flips via logical CSS properties.

**Consequences:**
- Toggling locale updates `dir` and all text with no network reload.
- No physical-direction CSS utilities are used (enforced by lint) — see project-context.md RTL hard rule.

---

## FR-29: Local content cache
The system can cache consumed content locally (IndexedDB via Dexie) so a student can continue during brief connectivity drops.

**Consequences:**
- A module fetched once is available from the local cache on a subsequent load with no network; cache invalidates when the module is republished.
- Dexie acts as write-behind buffer for student answers/atom completions. See **AD-6**.

## FR-30: Background sync of analytics
The system can queue analytics events offline and sync them when connectivity returns (Celery workers + Redis broker).

**Consequences:**
- Events captured offline are delivered to the backend after reconnection; no event is silently dropped.