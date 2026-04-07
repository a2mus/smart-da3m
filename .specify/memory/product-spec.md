# Product Specification: منصة إحسان — Plateforme Ihsane

**Generated**: 2026-04-07
**Version**: 1.0.0
**Status**: MVP Specification — Validated

---

## 1. Executive Summary

**Ihsane (إحسان)** is a web-based adaptive learning platform specialized in **intelligent pedagogical remediation** for the Algerian primary education system (ages 6–11). The platform detects learning gaps through adaptive diagnostic testing and delivers personalized remediation pathways aligned with Algeria's national curriculum.

Unlike existing EdTech platforms (Khan Academy, IXL, ALEKS), Ihsane is uniquely designed around four pillars: **pedagogical rigor** (AI-driven diagnostics and misconception analysis), **emotional safety** (an affective engine that detects frustration and provides calming interventions), **spiritual and value-based motivation** (rooted in Algerian cultural identity and the concept of Ihsane/إحسان), and **peer-to-peer solidarity** (Zakat al-Ilm — knowledge-sharing between students).

The MVP focuses on delivering the **diagnostic and remediation engine** with analytics dashboards for a closed pilot of < 500 students in 1–2 Algerian schools, validating the core adaptive algorithms before expanding to gamification, AI tutoring, and national deployment.

**Market opportunity**: No existing platform combines adaptive learning + Arabic RTL + French + Tamazight + offline-first + national curriculum alignment for any African or Arab primary education system. The target market extends to 12 million Algerian students, with expansion potential across the francophone and arabophone Maghreb.

---

## 2. Problem Statement

The Algerian education system ranks among the lowest globally in learning outcomes:

- **61.1% of students** are classified as "low performing" (PISA 2015)
- The Cour des Comptes (2024) rates educational results "parmi les plus bas au monde"
- Teachers lack tools for **individualized remediation** at scale
- **No adaptive learning platform** exists for the Algerian curriculum in any language
- The Arabic EdTech market is critically underserved: only **1.1% of websites** are in Arabic despite 240 million Arabic-speaking internet users

The core pedagogical problem: remediation in Algerian schools is traditionally delivered through repetitive drills ("traitement par répétition") rather than through targeted intervention on specific misconceptions. A student who confuses 1/4 > 1/2 (because 4 > 2) needs conceptual remediation on the relationship between denominator size and fraction value — not more fraction exercises.

---

## 3. Target Audience

### 3.1 Primary Users — Students (Élèves)

| Segment | Age | Grade (Algerian) | Key Needs |
|---------|-----|-------------------|-----------|
| Foundation | 6–7 | السنة 1 و 2 | Audio-heavy, icon-based UI, phonological awareness, basic numeracy |
| Transition | 8 | السنة 3 | Introduction of French, mathematical operations |
| Consolidation | 9–10 | السنة 4 و 5 | Integrative problem-solving methodology (الوضعيات الإدماجية) |

### 3.2 Secondary Users — Parents (الأولياء)

- Primarily access via **smartphone** (mobile-first dashboard)
- Need simplified pedagogical reports (competency-based, not just grades)
- Varying levels of digital literacy — interface must be available in Arabic and French
- Need actionable recommendations (e.g., "practice 5 min of mental arithmetic daily")

### 3.3 Administrative Users — Pedagogical Experts (الخبراء البيداغوجيون)

- Create, structure, and update modules, resources, and question banks
- Monitor student performance at aggregate level (class, school, wilaya)
- Adjust remediation algorithms and validate content alignment with national curriculum
- **Not live teachers** — the platform is an expert system, not a live instruction tool

---

## 4. Product Type & Platform

- **Type**: Web Application (SPA)
- **Framework**: Vue 3 + Vite (Composition API)
- **Target Platforms**: Modern browsers (Chrome, Firefox, Edge, Safari)
- **Architecture**: Hybrid offline-intelligent — pedagogical content cached offline via Workbox/Dexie.js, analytics and reports sync to cloud via Background Sync
- **Internationalization**: Bilingual MVP (Arabic RTL + French LTR) with vue-i18n, extensible to Tamazight and English
- **MVP Deployment**: OVH VPS (France/nearby) + Cloudflare Free CDN

---

## 5. Functional Requirements

### 5.1 Core Features (MVP)

#### F1 — Diagnostic Adaptatif (Adaptive Diagnostic Engine)

- Test initial of ~10 minutes per module (math or Arabic language)
- Adaptive question selection (inspired by EvidenceB's module-based adaptive testing)
- Error classification into three categories:
  - **Resource errors** (أخطاء الموارد): missing prerequisite knowledge
  - **Process errors** (أخطاء العمليات): misunderstanding instructions or methodology
  - **Incidental errors** (أخطاء عرضية): carelessness or lack of focus
- **Misconception detection** (inspired by Mindspark): identifies *why* the student errs, not just *what*
- Automatic placement into remediation groups:
  - **Group A** — Sufficient mastery → enrichment activities
  - **Group B** — Partial mastery → targeted gap remediation
  - **Group C** — No mastery → rebuild from scratch (intensive remediation)
- Student competency profile generated and updated after each session

#### F2 — Parcours de Remédiation (Conditional Remediation Pathways)

- Progression is **blocked** until the previous concept is mastered (inspired by Moodle conditional pathways)
- Three remediation modalities per difficulty type:
  - **Linguistic difficulties**: Audio-visual approach — interactive short stories + drag-and-drop correction
  - **Mathematical difficulties**: Virtual simulations — digital blocks, coins for number representation (concrete before abstract)
  - **Comprehension difficulties**: Simplified mind maps — tree-shaped colored visual summaries
- Content structured as **knowledge atoms** (micro-learning): if a student fails at "fraction subtraction," only the subtraction atom is re-presented, not the entire fractions module
- Dynamic difficulty adjustment: speed up if student responds too quickly (prevent boredom), simplify if student slows down (prevent frustration)
- Competency verification after remediation ("Passport" assessment):
  - **Pass**: Student earns a competency badge and advances
  - **Fail**: Pedagogical alert triggered for parents/experts with suggested in-person support plan
- Mastery levels (inspired by Khan Academy): Not Started → Attempted → Familiar → Proficient → Mastered
- Mastery can **regress** if student fails subsequent review assessments (models forgetting)

#### F3 — Dashboard Parent (Parent Dashboard — MVP)

- **Mobile-first responsive design** (smartphone access priority)
- Available in Arabic and French
- **Radar chart** showing student balance across core subjects (Arabic, Math, French)
- **Smart messages** instead of raw scores:
  - ❌ Not: "Math: 6/10"
  - ✅ Instead: "Your child excels at oral expression but needs help with taa marbouta spelling"
- **Strengths and gaps** clearly identified per competency
- **Smart recommendations**: actionable daily activities (e.g., "5 minutes of mental arithmetic")
- **Pedagogical alert notifications** when student is repeatedly blocked (> N failed attempts)
- Post-session summary notification (immediate, via email or in-app)
- Weekly progress report with visual trends

#### F4 — Alertes Pédagogiques (Pedagogical Alerts System)

- Triggered when a student:
  - Fails the same exercise type ≥ 3 consecutive times
  - Shows declining response speed (frustration indicator)
  - Fails a post-remediation validation assessment
  - Has not logged in for > N days
- Alerts delivered to:
  - **Parents**: simplified notification with recommended action
  - **Experts**: detailed diagnostic with suggested intervention strategy
- Alert severity levels: Info, Warning, Critical
- Auto-grouping suggestion for experts: students sharing the same error type are grouped for collective remediation

#### F5 — Back-office Experts (Expert Administration Panel)

- CRUD operations for:
  - **Modules** (matière → niveau → domaine → compétence — mirroring national curriculum structure)
  - **Resources** (micro-learning videos, interactive exercises, mind maps, stories)
  - **Question banks** with metadata: difficulty level, target competency, misconception targeted, estimated time
- Content structured per Algerian school years (السنة 1 through السنة 5)
- Content tagging: language (Arabic/French), age band (6–7, 8–9, 10–11), remediation type
- Preview mode: experts can simulate the student experience for any content
- Bulk import/export of question banks (CSV/JSON)
- Content versioning: track changes per module aligned with curriculum updates

#### F6 — Analytics Avancées (Advanced Analytics Dashboard)

- **Teacher/Expert level**:
  - **Competency Heatmap**: students × competencies matrix with color coding (Red/Yellow/Green for Not Mastered/Partial/Mastered)
  - **Auto-Grouping**: one-click generation of remediation groups based on shared error patterns
  - **Performance charts**: class progress toward national curriculum objectives
  - **Printable remediation cards** per student or group
- **Platform level**:
  - **Gap Reduction Rate**: % improvement between diagnostic and post-remediation assessments
  - **Mastery Speed**: average time to overcome a specific learning obstacle
  - **Retention Rate**: ability to solve similar problems 1 week after remediation
  - **Effort vs. Results**: time spent in remediation vs. actual improvement
  - **Resilience Score**: number of attempts before requesting help or abandoning
- Filterable by: student, class, school, grade level, subject, competency, time period
- Exportable reports (PDF, CSV)

### 5.2 Secondary Features (Post-MVP)

| Feature | Phase | Description |
|---------|-------|-------------|
| 🎮 Gamification (XP, badges, avatar) | Beta v2 | Points, medals ("Brave Trier", "Fraction Expert"), avatar progression |
| 🤝 Zakat al-Ilm (P2P) | Beta v2 | Top students record 30s audio tips for struggling peers |
| 🤖 Tuteur IA socratique | Beta v2 | Socratic chatbot (Arabic/French), never gives direct answers |
| 📱 PWA installable | Beta v2 | Home screen icon, full offline mode |
| 💖 Affective Engine | v2 | Mood check on login, frustration detection, calming interventions |
| 🏆 Leaderboard positif | v2 | "Most improved" ranking, team challenges |
| 📜 Miithaq al-Faris (Charter) | v2 | Spiritual/values onboarding pledge |
| 🏪 Pedagogic Store | v3 | XP converted to educational rewards |
| 🔬 Virtual Labs / AR | v3 | 3D manipulatives, augmented reality for math/science |
| 📺 Live Challenges | v3 | National competitions between wilayas |

### 5.3 Feature Prioritization (MoSCoW)

| Feature | Priority | Rationale |
|---------|----------|-----------|
| Adaptive diagnostic engine | **Must Have** | Core value proposition — without this, no platform |
| Conditional remediation pathways | **Must Have** | The "treatment" that follows the "diagnosis" |
| Parent dashboard (MVP) | **Must Have** | Parental involvement is critical for primary education |
| Pedagogical alerts | **Must Have** | Safety net — ensures no student falls through cracks |
| Expert back-office | **Must Have** | Content creation and management is foundational |
| Advanced analytics | **Must Have** | Proof of efficacy for pilot evaluation and scaling |
| Gamification | **Should Have** | High engagement impact but not required for core validation |
| P2P Zakat al-Ilm | **Should Have** | Unique differentiator but requires active user base |
| AI Tutor (Socratic) | **Should Have** | High value but complex — requires fine-tuning on Algerian content |
| PWA offline mode | **Should Have** | Critical for full deployment but pilot schools have connectivity |
| Affective Engine | **Could Have** | Innovative but can be simulated with static empathetic messages initially |
| Virtual Labs / AR | **Won't Have (MVP)** | Requires significant dev investment, better suited for post-validation |

---

## 6. Technical Decisions

### 6.1 Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Frontend** | Vue 3 + Vite | Vue 3.5+, Vite 6+ | Composition API, lightweight bundle < 200 KB, excellent RTL support via CSS logical properties |
| **Internationalization** | vue-i18n | 10+ | Bilingual Arabic (RTL) + French (LTR) with direction switching |
| **Offline Cache** | Workbox 7 + Dexie.js | 7.x, 4.x | Service worker caching, IndexedDB for local content storage, Background Sync for analytics |
| **Animations** | CSS transitions + Lottie | — | Lightweight gamification animations without CPU overhead on budget devices |
| **Backend API** | FastAPI + Python | 0.115+, 3.12+ | Async REST API, native Pydantic v2 validation, ML/AI ecosystem access |
| **Adaptive Engine** | scikit-learn + custom BKT | — | Bayesian Knowledge Tracing implementation, multi-arm bandit for exercise selection |
| **Database** | PostgreSQL | 16+ | JSONB for competency trees, full-text search for Arabic content, proven reliability |
| **Migrations** | Alembic | 1.13+ | Schema versioning and migration management |
| **Cache/Sessions** | Valkey | 8.x | Open-source Redis fork, session management, Celery broker, API response caching |
| **Async Tasks** | Celery + Valkey broker | 5.4+ | Offline sync processing, analytics aggregation, notification dispatch |
| **Hosting** | OVH VPS | — | Low latency from Algiers (< 20 ms), European data residency |
| **CDN** | Cloudflare Free | — | Global CDN, DDoS protection, SSL termination |
| **CI/CD** | GitHub Actions + Docker | — | Multi-stage Docker builds, automated deployment pipeline |
| **Containerization** | Docker + Docker Compose | — | Reproducible dev/staging/prod environments |

### 6.2 Data Architecture

- **Storage Model**: Hybrid offline-intelligent
  - **Offline (IndexedDB via Dexie.js)**: pedagogical content (exercises, resources, media), student progress cache, pending responses
  - **Cloud (PostgreSQL)**: user accounts, competency profiles, analytics data, content management, audit logs
  - **Sync**: Background Sync via Workbox — queued student responses and progress data uploaded when connectivity is available
- **Database Schema Key Entities**:
  - `users` (students, parents, experts) with role-based access
  - `curriculum` (matière → niveau → domaine → compétence hierarchy)
  - `modules` (content units with metadata)
  - `questions` (question banks with misconception tags)
  - `diagnostic_sessions` (test results with per-question analytics)
  - `remediation_paths` (generated pathways per student per competency)
  - `competency_profiles` (BKT state per student per competency)
  - `alerts` (pedagogical alerts with severity and status)
  - `analytics_events` (granular interaction tracking)

### 6.3 Authentication & Authorization

- **Three-tier authentication**:
  - **Students**: PIN code (4–6 digits), generated by parent during account creation. No email required. Session persistence via Valkey.
  - **Parents**: Email + password with optional phone verification. Manages child accounts.
  - **Experts**: Email + password with role-based permissions (content creator, analyst, admin).
- **Authorization**: Role-based access control (RBAC) with three roles (student, parent, expert)
- **Session Management**: JWT tokens (short-lived access + refresh tokens) stored server-side in Valkey
- **Security**: bcrypt password hashing, rate limiting on auth endpoints, CORS configured for production domain only

### 6.4 Deployment & Infrastructure

- **Hosting**: Single OVH VPS (4 vCPU, 8 GB RAM) for MVP pilot
- **Architecture**: Docker Compose stack (FastAPI app + PostgreSQL + Valkey + Celery worker + Nginx reverse proxy)
- **CI/CD Pipeline**: GitHub Actions — lint → test → build Docker images → deploy to VPS via SSH
- **CDN**: Cloudflare Free tier for static assets, SSL termination, and caching
- **Scale Target**: < 500 concurrent users for pilot phase
- **Monitoring**: Basic health checks + structured logging (JSON) to file, upgradeable to ELK/Grafana post-pilot
- **Backups**: Automated daily PostgreSQL dumps to OVH Object Storage

---

## 7. Non-Functional Requirements

### 7.1 Performance

- **Page load (initial)**: < 3 seconds on 3G connection
- **API response time**: < 200 ms (P95) for exercise serving
- **Diagnostic algorithm**: < 500 ms per question selection
- **Frontend bundle**: < 200 KB gzipped (Vue 3 + Vite tree-shaking)
- **Offline content**: Content modules cached < 5 MB each

### 7.2 Security

- All data in transit encrypted (TLS 1.3 via Cloudflare)
- Student data: minimal PII collection (name, grade, school — no photos, no biometrics)
- COPPA-inspired guardrails: parental consent required for account creation, no tracking for advertising
- Algerian data protection law compliance (Loi n° 18-07)
- Rate limiting on all public endpoints
- Input validation via Pydantic on all API endpoints

### 7.3 Reliability

- **Uptime target**: 99.5% (pilot phase)
- **Backup strategy**: Daily PostgreSQL backups, 30-day retention
- **Disaster recovery**: Full stack reproducible from Docker Compose + latest backup
- **Graceful degradation**: Offline mode serves cached content if backend is unreachable

### 7.4 Accessibility & Internationalization

- **RTL-first architecture**: CSS logical properties (inline-start/inline-end), mirrored layouts for Arabic
- **LTR switching**: Seamless direction change for French content
- **Audio support**: All instructions and feedback voiced for ages 6–8
- **Font choices**: Arabic-optimized fonts (Noto Sans Arabic, Amiri) + Latin fonts (Inter, Roboto)
- **Age-adapted interfaces**: Three visual variants targeting 6–7, 8–9, 10–11 age bands
- **Touch targets**: Minimum 60px for interactive elements (primary-age users)

### 7.5 Maintainability

- **Code standards**: ESLint + Prettier (frontend), Ruff + Black (backend)
- **Testing**: 80%+ coverage target (unit + integration)
- **API documentation**: Auto-generated OpenAPI/Swagger via FastAPI
- **File organization**: Feature-based (not type-based), < 400 lines per file

---

## 8. Constraints & Assumptions

### Constraints

| Constraint | Impact |
|-----------|--------|
| **Budget**: Solo developer / small team | Limits parallel development — sequential feature delivery |
| **Pilot scale**: < 500 students | Infrastructure can remain simple (single VPS) |
| **Algerian internet**: Variable connectivity | Offline-first architecture is non-negotiable for full launch (post-MVP) |
| **Tablettes ENIE**: Low-spec Android devices | Frontend must be extremely lightweight (< 200 KB bundle) |
| **Content creation**: Requires Algerian curriculum experts | Back-office must be intuitive for non-technical pedagogical experts |
| **Arabic NLP/ASR**: Limited pre-trained models for Algerian children's speech | Voice features deferred to post-MVP |

### Assumptions

- Pilot schools have basic Wi-Fi connectivity (sufficient for cloud-synced MVP)
- Pedagogical experts will populate content for at least one subject (Mathematics) and two grade levels (السنة 4 و 5) for MVP
- Parents have access to smartphones with mobile data for dashboard access
- The national curriculum structure is stable for the duration of the pilot

---

## 9. Success Metrics

### 9.1 Pilot Success Criteria (3-month evaluation)

| Metric | Target | Measurement Tool |
|--------|--------|-----------------|
| **Gap Reduction Rate** | ≥ 40% improvement post-diagnostic vs. post-remediation | Pre/post comparison algorithm |
| **Mastery Speed** | Average competency mastery within 3 remediation sessions | Remediation path analytics |
| **Retention Rate** | ≥ 70% of students retain mastery after 1 week | Delayed re-assessment |
| **Parent Engagement** | ≥ 60% of parents view dashboard weekly | Dashboard access logs |
| **Expert Adoption** | 100% of pilot experts create content via back-office | Back-office usage analytics |
| **Emotional Stability** | ≤ 30% session abandonment rate due to frustration | Behavioral tracking (response time patterns) |
| **System Reliability** | ≥ 99.5% uptime during pilot | Health check monitoring |

### 9.2 Business Validation

- Qualitative feedback from pilot teachers/experts confirming pedagogical value
- Parent satisfaction survey (NPS ≥ 30)
- Data sufficient to build a case for ministry partnership (P2IA model)

---

## 10. Out of Scope

The following items are **explicitly excluded** from this Product Specification and belong to separate documents:

| Item | Reason | Where it belongs |
|------|--------|-----------------|
| **UI/UX Design** | Visual design, wireframes, component library, interaction patterns | `ui-spec.md` (via `/speckit.uidesign`) |
| **Live teachers/tutoring** | The platform is an expert system, not a live instruction tool | Excluded by design (SDD) |
| **Complex serious gaming** | Deferred to post-pilot phase | Roadmap v2 |
| **Advanced collaboration tools** | Limited to simple P2P in future phases | Roadmap v2 |
| **iOS/Android native apps** | MVP is web-only | Roadmap v3 |
| **Tamazight/English content** | MVP focuses on Arabic + French bilingual | Roadmap v2 |
| **Voice recognition (ASR)** | Requires Algerian children's voice corpus that doesn't exist yet | Research phase |
| **AI-generated content** | Requires fine-tuning on Algerian curriculum | Roadmap v2 |
| **Multi-school/multi-wilaya deployment** | Pilot is 1–2 schools only | Post-pilot scaling plan |

---

## Appendix A: Roadmap Summary

| Phase | Focus | Duration (est.) |
|-------|-------|----------------|
| **MVP** | Diagnostic engine + remediation pathways + dashboards + back-office + analytics | 3–4 months |
| **Beta v2** | Gamification + P2P (Zakat al-Ilm) + AI Tutor + PWA offline | 2–3 months |
| **Full Launch v1** | All subjects + all grades + affective engine + full offline | 4–6 months |
| **v2** | Tamazight/English + AR/Virtual Labs + national competitions | 6+ months |

---

## Appendix B: Reference Documents

| Document | Description |
|----------|-------------|
| `مشروع_المنصة_التعليمية.md` | Complete pedagogical framework including diagnostic workflow, gamification, affective engine, Zakat al-Ilm, KPIs, and applied remediation examples |
| `SDD de la plateforme.md` | Software Design Document — vision, key features by user journey, excluded elements |
| `guide de conception.md` | Competitive analysis of 16 global platforms with detailed recommendations for Algerian context including algorithms, UX, gamification, offline, and AI innovations |

---

## Appendix C: Adaptive Algorithm Specification (MVP)

### C.1 Diagnostic Algorithm

The diagnostic uses a hybrid approach combining:

1. **Module-based adaptive testing** (EvidenceB model): ~10 questions per module, each question's difficulty selected based on previous answer correctness
2. **Misconception tagging** (Mindspark model): each question is tagged with potential misconceptions it can reveal
3. **Classification output**: Per-competency mastery level + identified misconceptions + recommended remediation group (A/B/C)

### C.2 Remediation Path Algorithm

1. **Bayesian Knowledge Tracing (BKT)**: Per-student, per-competency probability model tracking P(learned), P(guess), P(slip), P(transit)
2. **Multi-arm bandit** (EvidenceB model): Selects next exercise to maximize learning rate, balancing exploration (new exercise types) vs. exploitation (proven effective exercises for this student profile)
3. **Mastery threshold**: Configurable per competency (default: P(learned) ≥ 0.85 to be considered "Mastered")
4. **Regression check**: Periodic re-assessment — if P(learned) drops below 0.70, competency status is downgraded

### C.3 Alert Generation Rules

```
IF student.consecutive_failures(competency) >= 3:
    generate_alert(severity=WARNING, target=[parent, expert])

IF student.response_speed_trend == DECLINING AND student.accuracy < 0.5:
    generate_alert(severity=INFO, message="Possible frustration detected")

IF student.days_since_last_login > config.inactivity_threshold:
    generate_alert(severity=INFO, target=[parent])

IF student.post_remediation_assessment == FAILED:
    generate_alert(severity=CRITICAL, target=[parent, expert],
                   recommendation="In-person support recommended")
```
