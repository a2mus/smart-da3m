---
title: Ihsane Platform
created: 2026-07-09
updated: 2026-07-11
status: final
---

# PRD: Ihsane Platform
*Working title — confirm.*

## 0. Document Purpose

This PRD captures the product requirements for the **Ihsane** (إحسان) adaptive learning platform as it enters **pilot launch**. It is written for the PM (Mus), stakeholders, and the downstream BMad workflow owners (architecture → epics/stories → implementation).

**Ratification, not greenfield.** The MVP is already implemented (11 feature branches merged, deployed to `ihsan-dz.duckdns.org`). This document ratifies the existing implementation, formalizes scope boundaries (v1 vs v2/v3), and surfaces the open questions blocking pilot. It builds on three canonical sources — `README.md`, `مشروع_المنصة_التعليمية.md`, and `memory-bank/` — and does not duplicate them.

Structure: Glossary-anchored vocabulary (§3), features grouped with FRs nested under them (§4, globally numbered FR-1…FR-N), cross-cutting NFRs and constraints in their own sections, assumptions tagged inline and indexed (§9).

## 1. Vision

Ihsane is an intelligent, interactive pedagogical platform built specifically for **Algerian primary education (ages 6–11)**, aligned to the national curriculum. It diagnoses learning stumbling blocks precisely and accompanies each learner with **individualized remediation pathways** — therapeutic, not repetitive — across three pillars: **cognitive mastery, affective support, and a values dimension**.

The core reframe: turn "error" from a failure into a **"smart indicator for learning" (مؤشر ذكي للتعلم)**. Instead of drilling the same content, Ihsane routes the child to the smallest knowledge particle they missed, teaches it a different way, and verifies mastery before advancing. Parents and pedagogical experts are connected through decision-support dashboards — analytical, not overwhelming — so the whole ecosystem around the child moves together.

The aspiration is to be the **"first digital companion" of the Algerian student** — not a replacement for school or teacher, but a pedagogical and spiritual support that rehumanizes learning in the digital age. `[ASSUMPTION: the "spiritual companion" framing is vision-level; the v1 shipped product delivers the cognitive pedagogical core. The affective/values/spiritual layers (affective engine, Zakat al-Ilm, gamification) are v2 — see §6.]`

## 2. Target User

### 2.1 Jobs To Be Done

**Student (تلميذ), ages 6–11**
- *Functional:* Take an adaptive diagnostic; follow my personalized remediation pathway; verify mastery via the Passport; see my progress across competencies.
- *Emotional:* Feel safe making errors — errors are signals, not failure; learn at my own pace without test anxiety.
- *Contextual:* I may be pre-literate (Year 1–2) and need audio-read questions; I may be on a shared family device with intermittent connectivity.

**Parent / Guardian (ولي)**
- *Functional:* Understand where my child struggles in plain language (not raw scores); get a daily, doable reinforcement activity; receive an alert when something needs my attention.
- *Emotional:* Feel able to help even though I'm not a pedagogy specialist; feel proud of my child's progress.
- *Contextual:* I'm on a mobile phone, often in a hurry; I may manage more than one child.

**Expert (خبير — pedagogical expert / teacher)** `[ASSUMPTION: one role combining classroom analytics + content authoring, per Mus]`
- *Functional (classroom):* See my class's competency heatmap; auto-form remediation groups by shared gap; get early warning of students heading toward failure; print remediation cards.
- *Functional (authoring):* Author modules, build the question bank, and create knowledge atoms for remediation; bulk-import content; publish.
- *Emotional:* Feel supported in pedagogical decisions, not buried in raw data.

### 2.2 Non-Users (v1)

- Middle-school (متوسط) and secondary (ثانوي) students — framing context only in v1. `[ASSUMPTION: v1 is primary-tier only.]`
- Schools / users outside Algeria, or non-Algerian curricula.
- Users requiring Tamazight or English (v2).
- Users wanting live human tutoring or voice/ASR features (non-goal).

### 2.3 Key User Journeys

Named-protagonist narratives the product enables. FRs reference these by ID inline.

- **UJ-1. Maryam takes a diagnostic and gets a remediation pathway.**
  - **Persona + context:** Maryam, a Year-2 student (~7), is building foundational Arabic literacy on a shared family tablet.
  - **Entry state:** Logged in via PIN (no email for children). Audio-on (pre-literate). Comes from her student dashboard.
  - **Path:** (1) Taps "start challenge"; (2) the diagnostic serves questions adapted to her speed and accuracy; (3) she misses a phonological-awareness item; (4) the engine classifies the error and routes her to a remediation pathway of knowledge atoms taught a different way (concrete → abstract).
  - **Climax:** She works through the atoms, gets immediate feedback on why each step matters, and reaches the Passport competency task.
  - **Resolution:** She passes the Passport, earns the competency badge, and her mastery level advances. Next session continues from the new baseline. Realizes FR-9…FR-19.

- **UJ-2. Amine's mom checks the dashboard after an alert.**
  - **Persona + context:** Amine's mother, a non-specialist parent on her phone during a break.
  - **Entry state:** Authenticated via email+password. Pushed a `WARNING` pedagogical alert.
  - **Path:** (1) Opens the parent dashboard; (2) the radar chart shows Arabic weaker than Math; (3) the insight message reads "Amine excels in oral expression but needs help writing تاء مربوطة" (not "6/10"); (4) she reads today's daily recommendation — a 10-minute off-platform reinforcement activity.
  - **Climax:** She knows exactly what to do with her child today, in plain language.
  - **Resolution:** She encourages Amine in real life; next session his diagnostic reflects the reinforcement. Realizes FR-20…FR-22, FR-27.

- **UJ-3. Yacine's teacher forms a remediation group from the heatmap.**
  - **Persona + context:** Mr. Karim, an Expert who also teaches Year-5 math.
  - **Entry state:** Authenticated (email+password). Opens Expert analytics.
  - **Path:** (1) The competency heatmap shows 5 students red on "fractions"; (2) he taps auto-group; (3) the system clusters them into a remediation group by shared error type; (4) he prints remediation cards for the group.
  - **Climax:** He has a concrete, printable plan for tomorrow's differentiated session.
  - **Resolution:** He exports the report (PDF/CSV) for his records. Realizes FR-23…FR-26.

- **UJ-4. A content author loads Year-1 Arabic items.**
  - **Persona + context:** Ms. Lila, an Expert authoring curriculum content for the pilot.
  - **Entry state:** Authenticated. Opens the expert back-office.
  - **Path:** (1) Creates a module; (2) bulk-imports Year-1 Arabic question items; (3) attaches knowledge atoms to the items that target specific gaps; (4) previews-as-student, then publishes.
  - **Climax:** The pilot cohort can now access Year-1 Arabic diagnostics and remediation.
  - **Resolution:** Content is live and consumed by UJ-1. Realizes FR-5…FR-8.

## 3. Glossary

*Downstream workflows must use these terms exactly.*

- **Competency (كفاءة)** — A targeted skill/knowledge unit a student must master. Tracked individually via BKT. Cardinality: a module contains many competencies.
- **Resource (مورد)** — Foundational knowledge/prerequisite a competency depends on (e.g., the multiplication table). Numerator of the progress formula `Progress = (Learned Resources / Total Resources) × 100`.
- **Knowledge Atom (ذرة معرفية / كبسولة معرفية)** — The smallest unit of remediation content, addressing one concept gap. A lesson is split into atoms; only the failed atom is re-taught (micro-tagging).
- **Module** — A curriculum unit (e.g., "Year-1 Arabic — Phonological Awareness") grouping competencies, questions, and knowledge atoms.
- **Diagnostic Session** — An adaptive assessment that detects stumbling blocks and classifies errors.
- **Error Classification** — Three-way: **Resource error** (missing prerequisite), **Process error** (methodology breakdown), **Incidental error** (carelessness). Primary-tier refinement: **rule error** (doesn't know the rule) vs **mechanism error** (knows the rule, slips on execution).
- **Remediation Pathway (مسار المعالجة)** — A personalized sequence of knowledge atoms assigned to close a diagnosed gap. Therapeutic, not repetitive.
- **Passport (جواز المرور / مهمة كفاءة)** — The post-remediation competency task that verifies mastery. Deliberately not a hard test.
- **Competency Badge (وسام الكفاءة)** — Earned on Passport success; gates advancement.
- **Mastery Level (مستوى التمكن)** — One of: **Attempted → Familiar → Proficient → Mastered** (4-level scale, Khan-Academy-influenced). "Mastered" requires correct answers in a verification task after a time delay.
- **Bayesian Knowledge Tracing (BKT)** — The probabilistic algorithm tracking per-competency mastery, updated per response.
- **Heatmap (خريطة الحرارة)** — Students × competencies matrix; 🔴 not mastered / 🟡 partial / 🟢 mastered.
- **Remediation Group (فوج المعالجة)** — Auto-formed cluster of students sharing a gap profile.
- **Pedagogical Alert (تنبيه بيداغوجي)** — Notification on persistent difficulty. Severity: `INFO`, `WARNING`, `CRITICAL`.
- **Pillars** — The pedagogical dimensions the product spans. The README frames **three** (cognitive, affective, values); the master vision frames **four** (pedagogical, affective, spiritual, values). v1 delivers the cognitive/pedagogical pillar only; the rest are v2. See addendum §A4.
- **Year-band** — Algerian primary tier is grouped into Foundation (Y1–2), Transition (Y3), Consolidation (Y4–5).

## 4. Features

### 4.1 Authentication & Role-Based Access

**Description:** Three-tier access. Students log in with a **PIN** (no email for children); parents and experts log in with **email + password**. JWT sessions with refresh. Role-based access control gates every endpoint by role (STUDENT, PARENT, EXPERT). `[ASSUMPTION: sessions stored in Valkey; 30-minute access-token expiry, 7-day refresh — per backend config.]` Realizes UJ-1 (entry), UJ-2 (entry), UJ-3 (entry).

**Functional Requirements:**

#### FR-1: Student PIN login
A STUDENT can log in with a parent-linked PIN code (no email) so children access the platform without credentials they can't manage.

**Consequences (testable):**
- `POST /api/v1/auth/login/pin` with valid `{parent_email, pin_code}` returns a JWT; invalid PIN returns 401.
- A student account is always linked to exactly one parent (`parent_id`).

#### FR-2: Parent / Expert email-password login
A PARENT or EXPERT can log in with email + password (bcrypt-hashed) and receive a JWT pair (access + refresh).

**Consequences (testable):**
- `POST /api/v1/auth/login/email` issues access (30-min) and refresh (7-day) tokens.
- Passwords are stored bcrypt-hashed; plaintext never persisted or logged.

#### FR-3: Token refresh & session expiry
The system can refresh an expired access token using a valid refresh token; on refresh failure the client is logged out and redirected to login.

**Consequences (testable):**
- `POST /api/v1/auth/refresh` with a valid refresh token issues a new access token.
- A 401 on a protected route triggers one refresh attempt; on failure → logout + redirect to `Login?session_expired=true`.

#### FR-4: Role-based access control
The system can enforce per-endpoint authorization by role (STUDENT/PARENT/EXPERT) so each actor reaches only permitted resources.

**Consequences (testable):**
- An EXPERT endpoint called by a STUDENT token returns 403.
- A parent can read only their own children's data.

**Out of Scope:** Self-service password reset flows, OAuth/SSO (v2+).

### 4.2 Content Management (Expert Back-Office)

**Description:** Experts author curriculum content: modules, question-bank items, and knowledge atoms. Supports bulk import for loading pilot content. Realizes UJ-4.

**Functional Requirements:**

#### FR-5: Manage modules
An EXPERT can create, edit, and publish modules (curriculum units) scoped by subject and year-band.

**Consequences (testable):**
- An EXPERT can CRUD modules; a STUDENT/PARENT cannot (403).
- A module carries subject (Arabic/Math) and year-band (Y1–2 / Y3 / Y4–5) metadata.

#### FR-6: Manage question-bank items
An EXPERT can create and edit diagnostic question items linked to a competency, with correct-answer metadata and distractors.

**Consequences (testable):**
- A question item is always linked to exactly one competency and carries a difficulty level (1–10) and estimated time.
- An item with no correct-answer key is rejected on validation.

#### FR-7: Manage knowledge atoms
An EXPERT can create knowledge atoms (remediation micro-content) and attach them to competencies/items for targeted re-teaching.

**Consequences (testable):**
- A knowledge atom is typed (AUDIO_VISUAL / SIMULATION / MIND_MAP) and linked to a competency; that competency's remediation pathway can reference it.

#### FR-8: Bulk import content
An EXPERT can bulk-import modules/items/atoms (e.g., via structured file) to populate pilot content efficiently.

**Consequences (testable):**
- A bulk import for "Year-1 Arabic" creates the expected number of valid items; invalid rows are reported per-row without aborting the batch.

#### FR-8a: AI-assisted content drafting
An EXPERT can request an AI-drafted batch of question items and knowledge atoms from a stated Algerian-curriculum reference (subject, year-band, competency), review/edit them, and publish — a persistent authoring aid, not a one-time tool.

**Consequences (testable):**
- Given a curriculum reference, the system produces draft items mapped to the target competency; nothing the AI drafts is published without explicit expert review.
- AI-drafted content is always marked `DRAFT` until an EXPERT approves it (never auto-published).
- `[NOTE FOR PM: guardrails needed — output must align to the official Algerian curriculum, avoid hallucinated competencies, and respect the bilingual AR/FR requirement. See OQ-9.]`

**Notes:** This is a v1 expert-facing generative capability, distinct from the student-facing AI tutor (v2).

### 4.3 Pre-Literate Item Rendering

**Description:** The diagnostic and remediation surfaces must serve **pre-literate Year 1–2 children** — the pilot cohort — by reading questions aloud and offering picture-based answer options. The backend content model already supports media (`media_urls`, flexible `type`); this feature delivers the **frontend rendering**. Realizes UJ-1 (Maryam, pre-literate).

**Functional Requirements:**

#### FR-8b: Audio read-aloud of question text
The system can play an audio rendering of the question text (read-aloud) so a pre-literate STUDENT can understand the item without reading.

**Consequences (testable):**
- A question with audio media offers a play control; the audio is spoken in the item's language (AR/FR).
- Items intended for Y1–2 are flagged as requiring audio; the UI prompts the child to listen.

#### FR-8c: Image-choice item type
The system can render an `image_choice` item where answer options are images (not text) so a pre-literate STUDENT can respond by tapping pictures.

**Consequences (testable):**
- An `image_choice` question renders image buttons as options; the recorded answer maps back to the correct/incorrect evaluation like any other item type.
- The `multiple_choice`, `image_choice`, and `numeric` item types are supported end-to-end (author → render → score).

### 4.4 Adaptive Diagnostic Engine

**Description:** An adaptive assessment that selects and tunes questions per the learner, classifies errors, and feeds mastery tracking. BKT drives per-competency mastery; dynamic difficulty adapts to speed + accuracy. Realizes UJ-1.

**Functional Requirements:**

#### FR-9: Start / resume a diagnostic session
A STUDENT can start a diagnostic session for a module; the session can resume if interrupted (offline-tolerant).

**Consequences (testable):**
- `POST /api/v1/diagnostic/start` with `{module_id}` returns a `session_id`.

#### FR-10: Adaptive question selection (BKT-driven)
The system can select the next question based on the learner's current per-competency mastery estimate (BKT) so each session targets the information boundary.

**Consequences (testable):**
- Given a mastery estimate, the next-item selector returns an item whose difficulty targets the learner's ZPD (not a fixed sequence).

#### FR-11: Dynamic difficulty adjustment
The system can raise difficulty on fast correct answers and lower it on slow/incorrect answers to prevent boredom and frustration.

**Consequences (testable):**
- A correct answer with `response_time_ms` < 50% of the item's `estimated_time_sec` → next item difficulty increases by one step.
- An incorrect answer, or a correct answer slower than 150% of `estimated_time_sec` → next item difficulty decreases by one step.
- `[NOTE FOR PM: the 50%/150% bands are provisional defaults — tune from pilot data.]`

#### FR-12: Error classification
The system can classify each wrong answer as Resource / Process / Incidental error (with primary-tier rule-vs-mechanism refinement where applicable) to drive remediation routing.

**Consequences (testable):**
- A wrong answer is tagged with exactly one classification; the tag drives the remediation pathway chosen in FR-14.

#### FR-13: Capture response time
The system can record `response_time_ms` per answer; this feeds difficulty adaptation and frustration detection (affective engine, v2).

**Consequences (testable):**
- `POST /api/v1/diagnostic/answer` persists `{session_id, question_id, answer, response_time_ms}`.

### 4.5 Remediation Pathways

**Description:** A personalized sequence of knowledge atoms assigned to close a diagnosed gap, following a concrete → abstract progression, with spaced re-surfacing of failures. Realizes UJ-1.

**Functional Requirements:**

#### FR-14: Generate a remediation pathway
The system can generate a remediation pathway from a diagnostic result, sequencing knowledge atoms for the failed competencies and error type.

**Consequences (testable):**
- A diagnostic session that fails competency X yields a pathway containing atoms targeting X's gap, not the whole lesson.

#### FR-15: Deliver knowledge atoms (concrete → abstract)
A STUDENT can consume knowledge atoms that present the concept a different way, progressing from concrete/sensory to abstract.

**Consequences (testable):**
- For a math gap, the pathway can deliver an AUDIO_VISUAL or SIMULATION atom (concrete manipulatives) before any abstract symbolic item.
- An atom marked MIND_MAP is offered for comprehension-type gaps.

#### FR-16: Spaced re-surfacing of errors
The system can re-surface previously-failed items at spaced intervals to transfer learning to long-term memory.

**Consequences (testable):**
- An item failed today is eligible to reappear at a spaced interval (not immediately re-drilled).
- `[NOTE FOR PM: exact intervals (e.g., 1-day → 3-day → 7-day) and whether this is fully implemented are to be confirmed — see OQ-5/OQ-10.]`

### 4.6 Mastery & Passport Assessment

**Description:** A 4-level mastery model (Attempted → Familiar → Proficient → Mastered) and a Passport competency task that verifies mastery after remediation. Realizes UJ-1.

**Functional Requirements:**

#### FR-17: Track mastery level per competency
The system can maintain a 4-level mastery estimate per competency per student, updated from BKT and Passport outcomes.

**Consequences (testable):**
- A student's competency profile shows one of the four levels per competency; "Mastered" requires a delayed verification, not a single correct answer.
- `[NOTE FOR PM: BKT thresholds (e.g., P(learned) ≥ 0.95 → Mastered) and the "delayed" window are to be set — see OQ-5.]`

#### FR-18: Passport competency task
A STUDENT can attempt the Passport competency task at the end of a remediation pathway to verify mastery.

**Consequences (testable):**
- The Passport is offered only after the remediation pathway's atoms are completed; it is a single competency-scoped task, not a cumulative exam.
- Passport outcome (pass/fail) is persisted and drives FR-19.

#### FR-19: Award competency badge on Passport pass
On Passport success the system awards the competency badge and advances the student; on failure it raises a pedagogical alert (FR-27) and suggests an in-person support plan.

**Consequences (testable):**
- Passport pass → badge issued + next competency unlocked; Passport fail → alert raised at `WARNING` or higher and an in-person support suggestion surfaced to the parent/expert.

### 4.7 Parent Dashboard

**Description:** A mobile-first dashboard giving parents plain-language insight (not raw scores), a radar view of subject balance, and a daily reinforcement recommendation. Realizes UJ-2.

**Functional Requirements:**

#### FR-20: Subject-strength radar
A PARENT can view a radar chart of their child's mastery balance across subjects.

**Consequences (testable):**
- The radar renders one axis per subject with the child's average mastery level; a parent sees only their own child's radar.

#### FR-21: Smart insight messages (non-numeric)
The system can present strengths and gaps in functional language (e.g., "excels in oral expression but needs help writing تاء مربوطة") rather than numeric scores.

**Consequences (testable):**
- A parent dashboard view contains zero raw numeric scores as the primary signal; insights are sentence-form and use Glossary terms.

#### FR-22: Daily reinforcement recommendation
The system can show the parent one daily, off-platform reinforcement activity tied to the child's current gap.

**Consequences (testable):**
- Exactly one recommendation is shown per day, keyed to the child's most-recent failed competency; it is an off-platform (non-screen) activity.

### 4.8 Expert Analytics

**Description:** Decision-support analytics for the Expert: a competency heatmap, one-click auto-grouping into remediation groups, printable remediation cards, and report export. Realizes UJ-3.

**Functional Requirements:**

#### FR-23: Competency heatmap
An EXPERT can view a students × competencies heatmap (red/yellow/green) for their cohort.

**Consequences (testable):**
- Each cell maps a student's mastery level to a color: NOT_STARTED/ATTEMPTED → red, FAMILIAR → yellow, PROFICIENT/MASTERED → green.

#### FR-24: Auto-grouping into remediation groups
An EXPERT can auto-form remediation groups from the heatmap, clustering students by shared gap profile.

**Consequences (testable):**
- "Auto-group" returns groups whose members share a common failed competency / error type.

#### FR-25: Export reports (PDF / CSV)
An EXPERT can export analytics reports as PDF or CSV.

**Consequences (testable):**
- Export produces a downloadable PDF and CSV containing the heatmap data (student × competency × mastery level); CSV headers are stable and machine-parseable.

#### FR-26: Printable remediation cards
An EXPERT can print a remediation card per student/group for offline classroom use.

**Consequences (testable):**
- A remediation card is a print-formatted view containing the student(s), their failed competencies, and the recommended atoms — no interactive elements required to use it offline.

### 4.9 Pedagogical Alerts

**Description:** Smart notifications raised on persistent difficulty, with three severities, routed to parent and/or expert. Realizes UJ-2.

**Functional Requirements:**

#### FR-27: Generate pedagogical alerts
The system can raise an alert at severity `INFO` / `WARNING` / `CRITICAL` when a persistent/recurrent difficulty is detected, routed to the relevant parent and expert.

**Consequences (testable):**
- Repeated failure on the same competency within a window raises at least a `WARNING`.
- `[NOTE FOR PM: the exact trigger thresholds (how many failures, over what window → which severity) are underspecified — see OQ-4.]`

### 4.10 Bilingual Interface

**Description:** Arabic (RTL, primary) and French (LTR) UI with instant, no-reload switching, dedicated typography. Realizes UJ-1…UJ-3 (all surfaces).

**Functional Requirements:**

#### FR-28: Instant AR/FR language switch
A user can switch between Arabic (RTL) and French (LTR) instantly without a page reload; layout direction flips via logical CSS properties.

**Consequences (testable):**
- Toggling locale updates `dir` and all text with no network reload.
- No physical-direction CSS utilities are used (enforced by lint) — see project-context.md RTL hard rule.

### 4.11 Offline Support (foundation)

**Description:** A PWA foundation with local content caching (Dexie/IndexedDB) and background sync of analytics. `[ASSUMPTION: full offline-first is v2; v1 ships the caching foundation + sync, consistent with ADR-002 hybrid-offline.]` Realizes UJ-1 (connectivity edge cases).

**Functional Requirements:**

#### FR-29: Local content cache
The system can cache consumed content locally (IndexedDB via Dexie) so a student can continue during brief connectivity drops.

**Consequences (testable):**
- A module fetched once is available from the local cache on a subsequent load with no network; cache invalidates when the module is republished.

#### FR-30: Background sync of analytics
The system can queue analytics events offline and sync them when connectivity returns (Celery workers + Valkey broker).

**Consequences (testable):**
- Events captured offline are delivered to the backend after reconnection; no event is silently dropped.

**Feature-specific NFRs:**
- Full offline-first authoring/editing is out of v1 scope (v2).

## 5. Non-Goals (Explicit)

- **Not a school/teacher replacement** — a support, not a substitute.
- **Remediation is not repetition** — never re-drill the same content as "treatment."
- **No live human tutoring** (expert system only).
- **No gamification / peer-to-peer (Zakat al-Ilm) / AI tutor / affective engine in v1** — all v2.
- **No voice recognition / ASR.**
- **No native mobile apps** (PWA only in v1; native is v3).
- **No Tamazight or English** (v2).
- **No cutthroat competition** — leaderboards (when added in v2) rank "most improved," not top score.
- **No multi-school / multi-wilaya deployment** in the pilot (single-school pilot).

## 6. MVP Scope

### 6.1 In Scope (v1)

**Already built (ratified):**
- Auth & RBAC (PIN / email-password / JWT) — FR-1…FR-4
- Content management / expert back-office — FR-5…FR-8
- Adaptive diagnostic engine (BKT, adaptive selection, dynamic difficulty, error classification) — FR-9…FR-13
- Remediation pathways (pathway generation; spaced re-surfacing **to verify against code** — see OQ-10) — FR-14…FR-16
- 4-level mastery + Passport — FR-17…FR-19
- Parent dashboard (radar, insights, daily recommendation) — FR-20…FR-22
- Expert analytics (heatmap, auto-grouping, export, remediation cards) — FR-23…FR-26
- Pedagogical alerts (INFO/WARNING/CRITICAL) — FR-27
- Bilingual AR/FR RTL/LTR — FR-28
- Offline foundation (content cache + background sync) — FR-29…FR-30

**In v1 scope but NOT yet built (pilot-blocking):**
- AI-assisted content drafting (expert authoring aid) — FR-8a
- Pre-literate item rendering: audio read-aloud + image-choice items — FR-8b, FR-8c *(backend `media_urls` ready; frontend rendering to build)*

### 6.2 Out of Scope for MVP (deferred)

- **Gamification** (XP, badges hierarchy, avatar, pedagogic store, leaderboards) → **v2**.
- **Zakat al-Ilm** peer tutoring (voice tips, inspired-answers bank) → **v2**. `[NOTE FOR PM: emotionally load-bearing differentiator — revisit if pilot timeline permits.]`
- **AI tutor** (Socratic guided chatbot) → **v2**.
- **Affective engine** (mood check, frustration detection, "reflection pause") → **v2**. `[NOTE FOR PM: a named differentiator currently unbuilt — the biggest vision-vs-reality gap.]`
- **Deep adaptive learning** (Random Forest / NN), **Virtual Labs / AR**, **live national challenges** → **v3**.
- **Tamazight / English** → **v2**.
- **Native iOS/Android apps** → **v3**.

## 7. Success Metrics

*Each SM cross-references the FR(s) it validates. Targets adopted from the master-vision experimental KPI table; v2-tied targets marked forward-looking.*

**Primary**
- **SM-1**: Gap Reduction Rate — ≥ 40% median improvement in post- vs pre-diagnostic performance. Validates FR-9…FR-19.
- **SM-2**: Mastery Speed — median time to overcome a knowledge obstacle; provisional target **≤ 3 sessions** per obstacle, baselined from the first pilot cohort. Validates FR-17.
- **SM-3**: Retention — ≥ 70% of learners solve a similar integration situation one week after remediation. Validates FR-16, FR-18.

**Secondary**
- **SM-4**: Pilot engagement — ≥ 60% of students return within one week of their first session. Validates the UJ-1 loop.
- **SM-5**: Parent engagement — ≥ 50% of parents view the dashboard and act on at least one alert per month (UJ-2). Validates FR-20…FR-22, FR-27.
- **SM-6**: Accessibility — WCAG 2.1 AA, 0 violations on audited routes. Validates cross-cutting NFR.

**Forward-looking (v2-tied)**
- **SM-7** *(forward-looking)*: Zakat al-Ilm activation — 1-in-3 top students contributes (requires v2 feature).
- **SM-8** *(forward-looking)*: Emotional stability — 50% reduction in frustration drop-off after affective-engine calming (requires v2).
- **SM-9** *(forward-looking)*: Values engagement — 80% compliance with opening charter (requires v2 onboarding).

**Counter-metrics (do not optimize)**
- **SM-C1**: Raw time-on-platform — must NOT be optimized; longer sessions may indicate frustration, not learning. Counterbalances SM-4.
- **SM-C2**: Raw score inflation — must NOT be optimized by easing difficulty; a rising score with flat Gap Reduction means the diagnostic is gaming itself. Counterbalances SM-1.

## 8. Open Questions

1. **OQ-1 ✅ RESOLVED:** Privacy regime = **Algerian Law 18-07 + GDPR-K-style child principles** (parental consent, minimal collection, no profiling/ads, retention limits), hosted OVH/EU. Reflected in §11.
2. **OQ-2 🚫 launch-blocker:** Authentication/identity for the pilot — how are Year-1–2 children (pre-literate) onboarded and rostered to a parent and a class? `[ASSUMPTION: parent creates child accounts + PIN.]`
3. **OQ-3 ✅ RESOLVED:** Pre-literate rendering — build **audio read-aloud (FR-8b) + image-choice items (FR-8c)**. Backend `media_urls` already supports it; frontend rendering is the build. Pilot-blocker removed.
4. **OQ-4:** Pedagogical-alert trigger thresholds — how many failures, over what window, map to INFO vs WARNING vs CRITICAL?
5. **OQ-5:** Mastery-level BKT thresholds (e.g., P(mastery) ≥ 0.95 → "Mastered") and the delay rule for "Mastered" verification.
6. **OQ-6 ✅ RESOLVED:** Content is **AI-drafted from Algerian-curriculum references, then expert-reviewed** — and this is a **persistent v1 expert feature (FR-8a)**, not a one-time load. Pilot content (Y1–2 Arabic + Math) follows this flow.
7. **OQ-7 🚫 launch-blocker:** Pilot school selection and onboarding (1–2 Algerian schools) — no school onboarded yet; content not loaded.
8. **OQ-8:** Performance targets unverified on real hardware — `< 3 s on 3G`, `< 200 ms API P95`, bundle `< 200 KB`.
9. **OQ-9:** AI-assisted authoring guardrails — curriculum-alignment validation, hallucinated-competency prevention, bilingual AR/FR quality, and which LLM provider/hosting (data-residency implications under §11).
10. **OQ-10:** Verify against code whether **spaced re-surfacing (FR-16)** is actually implemented; memory-bank's implemented-feature list does not corroborate it. If absent, it belongs in §6.1 "not yet built."

## 9. Assumptions Index

*Every inline `[ASSUMPTION]` surfaced for confirmation:*
- §1 — Vision's "spiritual companion" framing is vision-level; v1 ships the cognitive core (affective/values layers = v2).
- §2.1 — "Expert" is one role combining classroom analytics + content authoring (per Mus).
- §2.2 — v1 is primary-tier only.
- §4.1 — Sessions in Valkey; 30-min access / 7-day refresh expiry (per backend config).
- §4.11 — Full offline-first is v2; v1 ships the cache + sync foundation (ADR-002).
- §6.2 — Affective engine is the biggest vision-vs-reality gap.
- §10 — Deeper logging/metrics are TBD (not documented in sources).
- §11 — OVH EU region (confirm in architecture).
- §11 — Cloudflare is DNS-only/origin-pull, not terminating TLS (confirm in architecture).

## 10. Cross-Cutting NFRs

- **Performance:** First contentful paint `< 3 s on 3G`; API P95 `< 200 ms`; frontend bundle `< 200 KB`. *[targets from memory-bank; unverified — OQ-8]*
- **Security:** JWT auth (30-min expiry), bcrypt password hashing, RBAC, rate limiting on auth endpoints, CORS allow-list, CSP headers. No secrets in the repo; `SECRET_KEY` overridden in prod.
- **Reliability:** `GET /health` endpoint for monitoring; pilot-level availability (single-school, < 500 users).
- **Observability:** Health check + structured error responses; `[ASSUMPTION: deeper logging/metrics TBD — not documented in sources.]`
- **Accessibility:** WCAG 2.1 AA, 0 violations on audited routes (axe-core audit in place; 6 routes audited).
- **Internationalization:** AR (RTL, primary) / FR (LTR); logical-CSS only (RTL hard rule).

## 11. Constraints & Guardrails

**Privacy (children's data) — RESOLVED (OQ-1): Algerian Law 18-07 + GDPR-K-style child principles:**
- **Regime:** Algerian Law 18-07 (2018) as the legal baseline, with GDPR-K-style enhanced protections for minors layered on top.
- **Consent:** Parental consent required to create any child account.
- **Minimal collection:** Collect only what the pedagogical loop requires (answers, response times, mastery estimates). No identity-profiling of children.
- **No advertising / no third-party tracking** on child-facing surfaces.
- **Retention limits:** Defined retention windows; secure deletion capability for a child's data on request.
- **Residency:** Data hosted on OVH (EU region). `[ASSUMPTION: OVH EU region — confirm in architecture.]`
- **CDN / TLS termination:** README and `memory-bank/techContext.md` list **Cloudflare** in front of OVH, while DEC-002 assigns TLS to Caddy/Let's Encrypt. `[ASSUMPTION: Cloudflare is DNS-only / origin-pull, not terminating TLS — confirm in architecture. If Cloudflare terminates TLS, child data transits a non-EU processor and needs a lawful basis under the regime above.]`
- **AI-assisted authoring (FR-8a):** any LLM provider must comply with the above; child-attributable data must not leave the residency boundary without a lawful basis. See OQ-9.

**Safety:**
- No user-generated content in v1 (voice tips / Zakat al-Ilm are v2), so UGC moderation is not yet required. When v2 ships, peer-audio moderation becomes mandatory.

**Cost:**
- Pilot runs on OVH VPS + DuckDNS (free DDNS); single-school scale (< 500 users). Tangible rewards (pedagogic store) are v2 and unfunded in v1.

**Compliance (accessibility):**
- WCAG 2.1 AA (built, audited). SCORM/xAPI portability and Quality Matters are aspirational (v2+).

**Platform:**
- Web PWA only in v1; mobile-first parent dashboard; tablet-optimized student surfaces. No native apps (v3).
