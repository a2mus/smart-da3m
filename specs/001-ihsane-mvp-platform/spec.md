# Feature Specification: Ihsane MVP Platform (منصة إحسان)

**Feature Branch**: `001-ihsane-mvp-platform`
**Created**: 2026-04-10
**Status**: Draft
**Input**: Build the Ihsane adaptive learning platform MVP — adaptive diagnostic engine, conditional remediation pathways, parent dashboard, pedagogical alerts, expert back-office, and advanced analytics for Algerian primary education (ages 6–11).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Expert Creates Content & Question Banks (Priority: P1)

A pedagogical expert logs into the back-office, creates a curriculum-aligned module for Mathematics (السنة 4), adds questions tagged with target competencies, difficulty levels, and targeted misconceptions. The expert previews the content as a student would experience it, then publishes the module for diagnostic and remediation use.

**Why this priority**: Without content, no diagnostic or remediation can function. Content creation is the foundational prerequisite for every other feature. The platform has zero value without a populated question bank.

**Independent Test**: Can be fully tested by creating a module with 10+ questions, tagging each with competency and misconception metadata, previewing in student mode, and verifying the content appears in the question bank with correct metadata.

**Acceptance Scenarios**:

1. **Given** an authenticated expert, **When** they create a new module under Mathematics → السنة 4 → Numbers & Operations → Addition, **Then** the module is saved with correct curriculum hierarchy and appears in the content listing.
2. **Given** an expert editing a question bank, **When** they add a question with difficulty level, target competency, misconception tag, and estimated time, **Then** all metadata is persisted and searchable.
3. **Given** a module with content, **When** the expert activates preview mode, **Then** they see the content exactly as a student would, including visual styling, interactions, and feedback.
4. **Given** multiple questions in a bank, **When** the expert exports the bank as CSV, **Then** the exported file contains all questions with complete metadata and can be re-imported without data loss.

---

### User Story 2 — Student Takes Adaptive Diagnostic (Priority: P1)

A student (age 9, السنة 4) logs in using their PIN code, selects Mathematics, and begins a ~10-minute adaptive diagnostic. The system selects questions dynamically based on previous answers, classifying errors as resource errors, process errors, or incidental errors. Upon completion, the student is placed into a remediation group (A, B, or C) and a competency profile is generated.

**Why this priority**: The diagnostic engine is the core value proposition — it determines what each student needs. Without accurate diagnosis, remediation is random and ineffective.

**Independent Test**: Can be fully tested by having a student complete a diagnostic session and verifying correct error classification, remediation group assignment, and competency profile generation.

**Acceptance Scenarios**:

1. **Given** a student with a valid PIN, **When** they enter the PIN on the login screen, **Then** they are authenticated and presented with their personalized dashboard.
2. **Given** a student starting a Math diagnostic, **When** they answer the first question correctly, **Then** the next question is of equal or higher difficulty; **When** they answer incorrectly, **Then** the next question probes the specific misconception area.
3. **Given** a student who answers "1/4 > 1/2 because 4 > 2", **When** this response is analyzed, **Then** the system classifies it as a resource error ("misconception about denominator-value relationship") rather than a generic "wrong answer."
4. **Given** a completed diagnostic session (~10 questions), **When** the results are processed, **Then** the student is assigned to Group A (mastery), Group B (partial — targeted remediation), or Group C (no mastery — intensive remediation) per competency.
5. **Given** a completed diagnostic, **When** the competency profile is generated, **Then** it includes per-competency mastery levels (Not Started → Attempted → Familiar → Proficient → Mastered) and identified misconceptions.

---

### User Story 3 — Student Follows Remediation Pathway (Priority: P1)

After diagnostic placement, a student assigned to Group B for "fraction subtraction" follows a personalized remediation pathway. The pathway uses micro-learning atoms — only the specific struggling concept is re-presented, not the entire module. The difficulty adjusts dynamically based on response speed and accuracy. Upon completing remediation, the student takes a "Passport" assessment to verify mastery.

**Why this priority**: Remediation is the "treatment" that follows the "diagnosis." Without it, the diagnostic is just a test with no corrective action.

**Independent Test**: Can be fully tested by placing a student in Group B for a specific competency, verifying they receive targeted micro-learning atoms, observing dynamic difficulty adjustment, and confirming the Passport assessment gates advancement.

**Acceptance Scenarios**:

1. **Given** a student placed in Group B for "fraction subtraction", **When** they begin remediation, **Then** only the "subtraction" knowledge atom is presented, not the full fractions module.
2. **Given** a student responding too quickly with high accuracy, **When** the system detects this pattern, **Then** difficulty increases to prevent boredom.
3. **Given** a student whose response speed is declining, **When** the system detects this pattern, **Then** difficulty simplifies and empathetic guidance is offered.
4. **Given** a student who completes the remediation exercises, **When** they take the Passport assessment and pass, **Then** they earn a competency badge, their mastery level advances, and they unlock the next concept.
5. **Given** a student who fails the Passport assessment, **When** the result is processed, **Then** a pedagogical alert is triggered for parents and experts, and the student is offered a revised remediation path.
6. **Given** a student who previously mastered a competency, **When** they fail a subsequent review assessment, **Then** their mastery level regresses (e.g., Proficient → Familiar) to model forgetting.

---

### User Story 4 — Parent Monitors Child Progress (Priority: P2)

A parent opens the dashboard on their smartphone, sees a warm greeting, and views a qualitative summary of their child's learning progress. Instead of raw scores, they see messages like "Your child excels at oral expression but needs help with taa marbouta spelling." They view a radar chart of subject balance, receive actionable daily recommendations, and get alerts when their child is struggling.

**Why this priority**: Parental involvement is critical in primary education, but parents should not be anxious — the dashboard must reassure while informing. This is essential for pilot buy-in but depends on diagnostic data (P1) to populate.

**Independent Test**: Can be fully tested by logging in as a parent, viewing a child's dashboard populated with diagnostic/remediation data, verifying qualitative messages render correctly, and confirming actionable recommendations are displayed.

**Acceptance Scenarios**:

1. **Given** a parent with a registered account, **When** they log in via email and password, **Then** they see a mobile-optimized dashboard with their child's name and avatar.
2. **Given** a child who has completed at least one diagnostic, **When** the parent views the dashboard, **Then** they see qualitative smart messages (e.g., strengths and areas for improvement) instead of raw numerical scores.
3. **Given** diagnostic data across multiple subjects, **When** the parent views the progress section, **Then** a radar chart displays subject balance across Arabic, Math, and French.
4. **Given** a child struggling with a specific skill, **When** the parent views recommendations, **Then** they see a specific, actionable daily activity (e.g., "5 minutes of mental arithmetic with coins").
5. **Given** a child who has been active, **When** the parent views recent activities, **Then** they see a bento grid of recent sessions (Dictation, Achievements, Stories) with timestamps.
6. **Given** the dashboard in Arabic mode, **When** rendered, **Then** all layout, text, and navigation flow correctly in RTL direction.

---

### User Story 5 — System Triggers Pedagogical Alerts (Priority: P2)

When a student fails the same exercise type 3+ consecutive times, shows declining response speed, fails a post-remediation assessment, or hasn't logged in for an extended period, the system automatically generates a pedagogical alert. Parents receive simplified notifications; experts receive detailed diagnostics with intervention strategies.

**Why this priority**: Alerts are the safety net — they ensure no student falls through the cracks. However, they require diagnostic and remediation data (P1) to trigger meaningfully.

**Independent Test**: Can be fully tested by simulating student failure patterns and verifying correct alert generation, severity classification, delivery to appropriate recipients, and auto-grouping suggestions.

**Acceptance Scenarios**:

1. **Given** a student who fails the same exercise type 3 consecutive times, **When** the system evaluates this pattern, **Then** a WARNING-level alert is generated and delivered to both parent and expert.
2. **Given** a student whose response speed is declining and accuracy is below 50%, **When** the system detects this, **Then** an INFO-level alert is generated noting "Possible frustration detected."
3. **Given** a student who fails a post-remediation Passport assessment, **When** the result is processed, **Then** a CRITICAL alert is generated with a recommendation for in-person support.
4. **Given** a student who hasn't logged in for more than N configured days, **When** the inactivity check runs, **Then** an INFO alert is sent to the parent.
5. **Given** multiple students sharing the same error type, **When** an expert views alerts, **Then** the system suggests auto-grouping these students for collective remediation.
6. **Given** a parent viewing an alert, **When** they open it, **Then** they see a simplified message with a clear recommended action (not technical jargon).

---

### User Story 6 — Expert Analyzes Student Performance (Priority: P2)

A pedagogical expert opens the analytics dashboard, views a competency heatmap showing all students' mastery levels across competencies, generates auto-grouped remediation clusters, reviews key performance indicators (gap reduction rate, mastery speed, retention rate), and exports a printable remediation card for a struggling student.

**Why this priority**: Analytics provide proof of efficacy for pilot evaluation and enable experts to intervene effectively. They depend on accumulated diagnostic and remediation data.

**Independent Test**: Can be fully tested by populating the system with mock student data, viewing the competency heatmap, triggering auto-grouping, and exporting reports.

**Acceptance Scenarios**:

1. **Given** an authenticated expert with a class of students, **When** they open the analytics dashboard, **Then** they see a competency heatmap (students × competencies) with Red/Yellow/Green color coding.
2. **Given** students with shared error patterns, **When** the expert clicks "Auto-Group", **Then** the system generates remediation groups based on common misconceptions.
3. **Given** a class with diagnostic and remediation data, **When** the expert views performance charts, **Then** they see class progress toward national curriculum objectives.
4. **Given** analytics data, **When** the expert views platform-level metrics, **Then** they see Gap Reduction Rate, Mastery Speed, Retention Rate, Effort vs. Results, and Resilience Score.
5. **Given** a specific student or group, **When** the expert requests a printable remediation card, **Then** a formatted document is generated with the student's profile, identified gaps, and recommended interventions.
6. **Given** any analytics view, **When** the expert applies filters (student, class, grade level, subject, competency, time period), **Then** all visualizations update to reflect the filtered data.
7. **Given** filtered analytics, **When** the expert clicks "Export", **Then** a report is generated in PDF or CSV format with the current view's data.

---

### User Story 7 — Bilingual Interface Switching (Priority: P3)

Any user (student, parent, or expert) can switch the platform interface between Arabic (RTL) and French (LTR) at any time. The entire layout, typography, navigation, and content direction adapt seamlessly.

**Why this priority**: Bilingual support is essential for the Algerian context but is a cross-cutting concern that enhances all other features rather than delivering standalone value.

**Independent Test**: Can be fully tested by switching language on any screen and verifying complete RTL/LTR adaptation including layout mirroring, font switching, and content translation.

**Acceptance Scenarios**:

1. **Given** a user on any screen in Arabic mode, **When** they switch to French, **Then** all UI text, labels, navigation, and layouts transition from RTL to LTR without page reload.
2. **Given** a parent dashboard in French (LTR), **When** viewing content, **Then** Arabic-optimized fonts (Tajawal, Cairo) are used for Arabic content blocks while Latin fonts (Plus Jakarta Sans, Inter) are used for French text.
3. **Given** a student on a tablet in Arabic mode, **When** using the interface, **Then** all touch targets remain at minimum 60px, and all interactive elements are mirrored correctly for RTL.

---

### Edge Cases

- What happens when a student loses internet during a diagnostic session? → Answers are cached locally and synced when connectivity restores; the session can continue offline.
- How does the system handle a student who abandons a diagnostic midway? → Progress is saved; the student can resume from where they left off.
- What happens when a parent has multiple children on the platform? → The dashboard supports context switching between children via the header.
- How does the system handle concurrent access to the same student account from multiple devices? → The most recent session takes priority; older sessions receive a notification.
- What if an expert bulk-imports a question bank with duplicate questions? → The system detects duplicates by content hash and flags them for review before import.
- How does the system handle a student who "games" the adaptive algorithm by intentionally failing to get easier questions? → The system tracks response time patterns; unnaturally fast incorrect answers are flagged as incidental errors.
- What happens when a student's competency profile is empty (first-time user)? → They are guided through an initial diagnostic before accessing any remediation.

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Access

- **FR-001**: System MUST support three distinct authentication methods — PIN code (4–6 digits) for students, email+password for parents, email+password with role-based permissions for experts.
- **FR-002**: System MUST enforce role-based access control (RBAC) with three roles: student, parent, expert — each with distinct feature access.
- **FR-003**: Parents MUST be able to create and manage child accounts, generating unique PIN codes for each child.
- **FR-004**: System MUST manage sessions via short-lived access tokens with refresh tokens.
- **FR-005**: System MUST enforce rate limiting on all authentication endpoints to prevent brute-force attacks.

#### Diagnostic Engine

- **FR-010**: System MUST deliver adaptive diagnostic tests of approximately 10 questions per module, dynamically selecting questions based on previous answers.
- **FR-011**: System MUST classify student errors into three categories: resource errors (missing prerequisites), process errors (methodology misunderstanding), and incidental errors (carelessness).
- **FR-012**: System MUST detect specific misconceptions by analyzing error patterns, not just correctness.
- **FR-013**: System MUST automatically place students into remediation groups (A: mastery/enrichment, B: partial/targeted remediation, C: no mastery/intensive remediation) per competency.
- **FR-014**: System MUST generate and continuously update a per-student competency profile with mastery levels (Not Started → Attempted → Familiar → Proficient → Mastered).
- **FR-015**: System MUST implement Bayesian Knowledge Tracing (BKT) to maintain per-student, per-competency probability models.

#### Remediation Pathways

- **FR-020**: System MUST block progression until the prerequisite concept is mastered (conditional pathways).
- **FR-021**: System MUST deliver remediation as micro-learning "knowledge atoms" — targeting only the specific struggling concept.
- **FR-022**: System MUST support three remediation modalities: audio-visual (stories + drag-and-drop), virtual simulations (digital blocks, coins), and simplified mind maps.
- **FR-023**: System MUST dynamically adjust difficulty based on student response speed and accuracy patterns.
- **FR-024**: System MUST provide "Passport" assessments after remediation to verify mastery before advancing.
- **FR-025**: System MUST support mastery regression — downgrading mastery level if a student fails subsequent review assessments.
- **FR-026**: System MUST use multi-arm bandit selection to choose exercises that maximize learning rate.

#### Parent Dashboard

- **FR-030**: System MUST provide a mobile-first responsive dashboard for parents.
- **FR-031**: System MUST display qualitative smart messages instead of raw numerical scores.
- **FR-032**: System MUST display a radar chart showing student balance across core subjects.
- **FR-033**: System MUST provide actionable daily recommendations based on identified learning gaps.
- **FR-034**: System MUST display recent learning activities in a visual format.
- **FR-035**: System MUST support post-session summary notifications and weekly progress reports.
- **FR-036**: System MUST allow parents with multiple children to switch between child profiles.

#### Pedagogical Alerts

- **FR-040**: System MUST generate alerts when a student fails the same exercise type ≥ 3 consecutive times.
- **FR-041**: System MUST generate alerts when declining response speed combined with low accuracy indicates frustration.
- **FR-042**: System MUST generate alerts when a student fails a post-remediation Passport assessment.
- **FR-043**: System MUST generate alerts when a student hasn't logged in for more than a configurable number of days.
- **FR-044**: System MUST classify alerts into three severity levels: Info, Warning, Critical.
- **FR-045**: System MUST deliver simplified notifications to parents and detailed diagnostics to experts.
- **FR-046**: System MUST suggest auto-grouping of students sharing the same error type for collective remediation.

#### Expert Back-Office

- **FR-050**: System MUST support CRUD operations for curriculum modules following the national structure (matière → niveau → domaine → compétence).
- **FR-051**: System MUST support CRUD operations for resources (videos, interactive exercises, mind maps, stories).
- **FR-052**: System MUST support CRUD operations for question banks with metadata (difficulty, competency, misconception, estimated time).
- **FR-053**: System MUST support content tagging by language, age band, and remediation type.
- **FR-054**: System MUST provide a preview mode allowing experts to simulate the student experience.
- **FR-055**: System MUST support bulk import and export of question banks in CSV and JSON formats.
- **FR-056**: System MUST support content versioning to track changes aligned with curriculum updates.

#### Analytics

- **FR-060**: System MUST display a competency heatmap (students × competencies) with Red/Yellow/Green color coding.
- **FR-061**: System MUST provide one-click auto-grouping of students based on shared error patterns.
- **FR-062**: System MUST display platform-level metrics: Gap Reduction Rate, Mastery Speed, Retention Rate, Effort vs. Results, Resilience Score.
- **FR-063**: System MUST support filtering by student, class, school, grade level, subject, competency, and time period.
- **FR-064**: System MUST support export of reports in PDF and CSV formats.
- **FR-065**: System MUST generate printable remediation cards per student or group.

#### Internationalization

- **FR-070**: System MUST support bilingual interface in Arabic (RTL) and French (LTR) with seamless switching.
- **FR-071**: System MUST use CSS logical properties for all layout to ensure proper RTL/LTR rendering.
- **FR-072**: System MUST use Arabic-optimized fonts (Tajawal, Cairo) for Arabic content and Latin fonts (Plus Jakarta Sans, Inter) for French/numeric content.

### Key Entities

- **User**: Represents any person interacting with the platform. Has a role (student, parent, expert), authentication method (PIN or email+password), and language preference (Arabic/French).
- **Student Profile**: The learner's identity linked to a parent account. Contains grade level, school, and the parent-generated PIN.
- **Competency Profile**: Per-student, per-competency state tracking mastery level and BKT probabilities (P(learned), P(guess), P(slip), P(transit)). Updated after every interaction.
- **Curriculum Module**: A hierarchical content unit following matière → niveau → domaine → compétence. Contains version history and curriculum alignment metadata.
- **Question**: An individual assessment item within a question bank. Tagged with difficulty level, target competency, targeted misconception, estimated response time, and language.
- **Diagnostic Session**: A record of a student's adaptive diagnostic test, including per-question analytics (response, time, correctness, error classification).
- **Remediation Path**: A generated personalized learning pathway for a student on a specific competency, containing ordered knowledge atoms and gated Passport assessments.
- **Knowledge Atom**: The smallest unit of remediation content — a micro-learning activity targeting a single concept or skill.
- **Pedagogical Alert**: A system-generated notification triggered by student behavioral patterns, with severity (Info/Warning/Critical), target recipients, and recommended action.
- **Analytics Event**: A granular interaction record (response submitted, exercise started, session completed) used for aggregate analytics computation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students complete a diagnostic assessment in under 10 minutes per module.
- **SC-002**: ≥ 40% improvement in competency scores between initial diagnostic and post-remediation assessment (Gap Reduction Rate).
- **SC-003**: Average student achieves competency mastery within 3 remediation sessions per competency (Mastery Speed).
- **SC-004**: ≥ 70% of students retain mastery when re-assessed 1 week after remediation (Retention Rate).
- **SC-005**: ≤ 30% of sessions are abandoned mid-exercise due to frustration (Emotional Stability).
- **SC-006**: ≥ 60% of parents view the dashboard at least once per week (Parent Engagement).
- **SC-007**: 100% of pilot experts successfully create and publish content via the back-office (Expert Adoption).
- **SC-008**: Platform achieves ≥ 99.5% uptime during the 3-month pilot (System Reliability).
- **SC-009**: All pages load in under 3 seconds on a 3G connection (Performance).
- **SC-010**: Parent NPS score ≥ 30 in post-pilot satisfaction survey (User Satisfaction).
- **SC-011**: System supports < 500 concurrent users without performance degradation (Scale Target).
- **SC-012**: The platform functions correctly in both Arabic (RTL) and French (LTR) modes with no layout broken elements (Bilingual Compliance).

## Assumptions

- Pilot schools (1–2 in Algeria) have basic Wi-Fi connectivity sufficient for cloud-synced operations; full offline mode is deferred to post-MVP.
- Pedagogical experts will populate content for at least Mathematics and two grade levels (السنة 4 and السنة 5) before the pilot begins.
- Parents have access to smartphones with mobile data for dashboard access.
- The Algerian national curriculum structure (matière → niveau → domaine → compétence) is stable for the duration of the pilot.
- Students are familiar with basic tablet/computer interactions appropriate for their age group.
- The existing reference documents (مشروع_المنصة_التعليمية.md, SDD, guide de conception) provide sufficient pedagogical framework for implementing remediation strategies.
- Audio-based instructions and feedback for ages 6–8 will use pre-recorded audio clips, not text-to-speech synthesis.
- The platform will be deployed on an OVH VPS with Cloudflare CDN providing < 20ms latency from Algiers.
- No voice recognition (ASR) features are included in the MVP.
- Gamification elements (XP, badges, leaderboards) beyond basic competency badges are deferred to post-MVP.
