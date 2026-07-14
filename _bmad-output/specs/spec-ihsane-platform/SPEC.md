---
id: SPEC-ihsane-platform
companions:
  - glossary.md
  - functional-requirements.md
  - ../../planning-artifacts/architecture/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/architecture/ARCHITECTURE-WALKTHROUGH.md
  - ../../project-context.md
sources:
  - ../../planning-artifacts/prds/prd-moody-bird-2026-07-09/prd.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability only — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Ihsane Platform

## Why

Algerian primary students (ages 6–11) stumble on learning obstacles that go undetected until they compound into failure. Traditional remediation is repetitive drilling, not therapeutic. Ihsane reframes error as a "smart indicator for learning" (مؤشر ذكي للتعلم): the platform diagnoses the exact knowledge gap, routes the child to the smallest particle they missed, teaches it a different way, and verifies mastery before advancing — connecting pedagogues and parents through decision-support dashboards so the ecosystem around the child moves together.

The platform is converging to V1 (pilot launch). The MVP is already implemented (11 feature branches merged); this spec ratifies the existing implementation, formalizes scope boundaries, and incorporates the architectural decisions (AD-1 through AD-7) that the architecture spine locked.

## Capabilities

- **CAP-1: Authentication & Role-Based Access**
  - **intent:** Users can authenticate by role (PIN for students, email+password for parents/experts) and reach only permitted resources.
  - **success:** A student logs in with PIN, a parent with email+password, an expert with email+password; cross-role access returns 403. FR-1..FR-4.

- **CAP-2: Content Authoring (Expert Back-Office)**
  - **intent:** An expert can create, edit, bulk-import, and AI-draft curriculum content (modules, questions, knowledge atoms) for pilot deployment.
  - **success:** An expert authors a module, attaches questions and atoms, bulk-imports a batch, and AI-drafts items from a curriculum reference; all AI-drafted content is marked DRAFT until expert-approved. FR-5..FR-8a.

- **CAP-3: Pre-Literate Item Rendering**
  - **intent:** Pre-literate Year 1–2 students can take diagnostics via audio read-aloud and image-choice answer options.
  - **success:** A question with audio media plays a control; an `image_choice` question renders image buttons that map to correct/incorrect evaluation. FR-8b, FR-8c.

- **CAP-4: Adaptive Diagnostic Engine**
  - **intent:** The system can run an adaptive assessment that selects questions based on BKT mastery estimates, adjusts difficulty dynamically, classifies errors, and captures response times.
  - **success:** A diagnostic session selects items targeting the learner's ZPD, raises/lowers difficulty based on speed+accuracy, and tags each wrong answer with exactly one error classification. FR-9..FR-13. Governed by **AD-1** (stateless engine), **AD-7** (loop stage 2–3).

- **CAP-5: Remediation Pathway Generation & Delivery**
  - **intent:** The system can generate a personalized remediation pathway from diagnostic gaps using hybrid AI (deterministic selection + LLM augmentation), validated by an expert, and deliver atoms to the student in a concrete→abstract progression.
  - **success:** A failed diagnostic yields a pathway targeting the specific gap; the pathway enters PROPOSED state, is reviewed by an expert, and the student follows validated atoms. FR-14..FR-16. Governed by **AD-2** (state machine), **AD-3** (hybrid AI), **AD-7** (loop stage 4–6).

- **CAP-6: Mastery & Passport Assessment**
  - **intent:** The system can track 4-level mastery per competency and verify mastery via a Passport competency task after remediation, awarding badges or triggering re-remediation.
  - **success:** A student who passes the Passport earns the competency badge and advances; a student who fails triggers a pedagogical alert and a new remediation proposal (loop iterates). FR-17..FR-19. Governed by **AD-2** (PASSPORT_TESTING → DIAGNOSED on fail).

- **CAP-7: Parent Monitoring Dashboard**
  - **intent:** A parent can view their child's evolution (radar chart, plain-language insights, daily reinforcement recommendation, alerts) in real time without needing pedagogical expertise.
  - **success:** A parent sees zero raw numeric scores as primary signals, receives one daily off-platform activity recommendation, and gets real-time SSE alerts on persistent difficulty. FR-20..FR-22. Governed by **AD-5** (SSE push), **AD-6** (read cache).

- **CAP-8: Expert Analytics**
  - **intent:** An expert can view a competency heatmap, auto-form remediation groups, export reports, and print remediation cards for offline classroom use.
  - **success:** A heatmap renders student×competency with red/yellow/green; auto-grouping clusters students by shared gap; PDF/CSV export works; remediation cards are print-formatted. FR-23..FR-26.

- **CAP-9: Pedagogical Alerts**
  - **intent:** The system can raise severity-tiered alerts (INFO/WARNING/CRITICAL) on persistent difficulty, pushed in real time to parents and experts via SSE.
  - **success:** Repeated failure on the same competency raises at least WARNING; the alert is delivered via SSE push with a simplified message for parents and a detailed message for experts. FR-27. Governed by **AD-5** (SSE).

- **CAP-10: Bilingual Interface**
  - **intent:** Users can switch between Arabic (RTL, primary) and French (LTR) instantly without page reload, using logical CSS only.
  - **success:** Toggling locale updates `dir` and all text with no network reload; no physical-direction CSS utilities pass the linter. FR-28.

- **CAP-11: Offline Support (PWA Foundation)**
  - **intent:** Students can continue diagnostic and remediation work during connectivity drops, with answers and completions queued and synced on reconnect.
  - **success:** A module fetched once is available offline; offline-captured events are delivered after reconnection with no silent drops. FR-29..FR-30. Governed by **AD-6** (write-behind Dexie for students, online-first for experts/parents).

- **CAP-12: Multi-Tenant Isolation**
  - **intent:** The platform can host multiple organizations (establishments) on the same deployment with complete data isolation between tenants.
  - **success:** A user in Organization A cannot read or write Organization B's data; every query is automatically tenant-filtered via middleware. Governed by **AD-4**.

## Constraints

- **AD-1 — Database is the single source of truth.** No engine may hold domain state in memory between calls. Engines are pure functions. Rules out in-memory state caches, dual ownership.
- **AD-2 — Remediation path lifecycle is an explicit state machine.** DIAGNOSED → PROPOSED → VALIDATED → IN_PROGRESS → COMPLETED, with ABANDONED and PASSPORT_TESTING branches. Transitions enforced in the service layer. Rules out direct status manipulation from API layer, skipping the expert validation gate.
- **AD-3 — Hybrid AI for remediation proposals.** Deterministic atom selection + LLM augmentation + expert validation. LLM is never in the synchronous request path; all LLM calls go through Celery. Rules out pure-LLM unpredictability and pure-deterministic rigidity.
- **AD-4 — Multi-tenant isolation via Organization entity.** Every tenant-scoped model carries `organization_id`. Tenant filtering is automatic via middleware, never manual. Rules out cross-tenant data leakage, ad-hoc per-query filtering.
- **AD-5 — Push notifications via SSE.** Server-Sent Events over `/api/v1/events/stream`, backed by Redis Pub/Sub per tenant. Rules out polling-based notification delivery.
- **AD-6 — Offline-first for students, online-first for experts and parents.** Dexie write-behind buffer for student answers/atom completions; online required for expert authoring/validation and parent mutations. Rules out full offline for all roles, unnecessary online requirement for students.
- **AD-7 — Core domain loop is the organizing principle.** Every feature maps to a stage: AUTHOR → DIAGNOSE → DETECT → PROPOSE → VALIDATE → REMEDIATE → ASSESS → MASTER. Rules out features that don't attach to the loop.
- **Privacy — Algerian Law 18-07 + GDPR-K-style child protections.** Parental consent for child accounts, minimal collection, no advertising or third-party tracking on child surfaces, retention limits, data hosted on OVH EU region. see constraints companion in PRD §11.
- **RTL/LTR — Logical CSS only.** Physical-direction Tailwind utilities (`pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`, etc.) are banned; logical equivalents (`ps-*`, `pe-*`, `start-*`, `end-*`) are required. Enforced by ESLint.
- **Wire format — snake_case on the wire, camelCase in TS.** The Axios service layer (`src/services/api.ts`) is the sole translation boundary; components never handle snake_case.
- **Async backend — Never block the event loop.** All DB calls and I/O must be async (SQLAlchemy 2.0 async, asyncpg).
- **PWA only in V1 — No native mobile apps.** PWA with vite-plugin-pwa + Dexie (IndexedDB).

## Non-goals

- Not a school or teacher replacement — a support, not a substitute.
- Remediation is not repetition — never re-drill the same content as "treatment."
- No live human tutoring (expert system only).
- No gamification, peer-to-peer (Zakat al-Ilm), AI tutor, or affective engine in V1 — all V2.
- No voice recognition / ASR.
- No native mobile apps (PWA only in V1; native is V3).
- No Tamazight or English (V2).
- No cutthroat competition — leaderboards (V2) rank "most improved," not top score.

## Success signal

- **SM-1:** Gap Reduction Rate — ≥ 40% median improvement in post- vs pre-diagnostic performance.
- **SM-2:** Mastery Speed — median ≤ 3 sessions to overcome a knowledge obstacle.
- **SM-3:** Retention — ≥ 70% of learners solve a similar integration situation one week after remediation.
- **SM-4:** Pilot engagement — ≥ 60% of students return within one week of their first session.
- **SM-5:** Parent engagement — ≥ 50% of parents view the dashboard and act on at least one alert per month.
- **SM-6:** Accessibility — WCAG 2.1 AA, 0 violations on audited routes.

**Counter-metrics (do not optimize):**
- **SM-C1:** Raw time-on-platform — must NOT be optimized; longer sessions may indicate frustration.
- **SM-C2:** Raw score inflation — must NOT be optimized by easing difficulty; rising score with flat Gap Reduction means the diagnostic is gaming itself.

## Assumptions

- Vision's "spiritual companion" framing is vision-level; V1 ships the cognitive core (affective/values layers = V2).
- "Expert" is one role combining classroom analytics + content authoring (per Mus).
- V1 is primary-tier only (ages 6–11, Algerian curriculum).
- Sessions in Redis; 30-min access / 7-day refresh expiry (per backend config).
- Full offline-first is V2; V1 ships the cache + sync foundation (AD-6 defines the boundary).
- Affective engine is the biggest vision-vs-reality gap.
- OVH EU region for data residency (confirm in deployment).
- Cloudflare is DNS-only/origin-pull, not terminating TLS (confirm in architecture — if Cloudflare terminates TLS, child data transits a non-EU processor and needs a lawful basis).

## Open Questions

- **OQ-4:** Pedagogical-alert trigger thresholds — how many failures, over what window, map to INFO vs WARNING vs CRITICAL?
- **OQ-5:** Mastery-level BKT thresholds (e.g., P(learned) >= 0.95 -> Mastered) and the delay rule for "Mastered" verification.
- **OQ-8:** Performance targets unverified on real hardware — < 3s on 3G, < 200ms API P95, bundle < 200KB.
- **OQ-9:** AI-assisted authoring guardrails — curriculum-alignment validation, hallucinated-competency prevention, bilingual AR/FR quality.
- **OQ-10:** Verify against code whether spaced re-surfacing (FR-16) is actually implemented; if absent, it belongs in "not yet built."

## Resolved Questions

- **OQ-2 RESOLVED:** Parent creates child accounts + PIN.
- **OQ-7 RESOLVED:** Pilot school onboarding is a logistics/partnership task (not technical): (1) select 1–2 Algerian primary schools, (2) onboard their pédagogues as Expert accounts in their Organization, (3) ensure Y1–2 Arabic + Math content is authored/imported/AI-drafted. Multi-tenant architecture (AD-4) supports this from day one.
- **OQ-Arch-1 RESOLVED:** LiteLLM as the LLM gateway. Configurable base URL + API key in settings. For testing, fix a default model from existing subscriptions. Provider is swappable via config change.
- **OQ-Arch-2 RESOLVED:** Shared content (validated knowledge atoms, remediation templates, tests/modules) is platform-level with `is_shared=True` — all orgs can read. Personal data (sessions, answers, paths, mastery, alerts) is strictly tenant-scoped, never shareable.
- **OQ-Arch-3 RESOLVED:** SSE confirmed viable with FastAPI + Caddy. Add `sse-starlette` dependency; exclude SSE endpoint from Caddy's `encode gzip zstd` block (compression buffers streaming). Caddy reverse_proxy handles long-lived connections by default.