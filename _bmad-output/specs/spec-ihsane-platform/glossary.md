# Glossary — Ihsane Platform

*Downstream workflows must use these terms exactly. Preserved from PRD §3.*

- **Competency (كفاءة)** — A targeted skill/knowledge unit a student must master. Tracked individually via BKT. A module contains many competencies.
- **Resource (مورد)** — Foundational knowledge/prerequisite a competency depends on (e.g., multiplication table). Numerator of progress: `Progress = (Learned Resources / Total Resources) × 100`.
- **Knowledge Atom (ذرة معرفية)** — The smallest unit of remediation content, addressing one concept gap. Only the failed atom is re-taught (micro-tagging).
- **Module** — A curriculum unit (e.g., "Year-1 Arabic — Phonological Awareness") grouping competencies, questions, and knowledge atoms.
- **Diagnostic Session** — An adaptive assessment that detects stumbling blocks and classifies errors.
- **Error Classification** — Three-way: **Resource error** (missing prerequisite), **Process error** (methodology breakdown), **Incidental error** (carelessness). Primary-tier refinement: **rule error** vs **mechanism error**.
- **Remediation Pathway (مسار المعالجة)** — A personalized sequence of knowledge atoms assigned to close a diagnosed gap. Therapeutic, not repetitive. Lifecycle governed by **AD-2** in the Architecture Spine.
- **Passport (جواز المرور)** — The post-remediation competency task that verifies mastery. Deliberately not a hard test.
- **Competency Badge (وسام الكفاءة)** — Earned on Passport success; gates advancement.
- **Mastery Level (مستوى التمكن)** — One of: **Attempted → Familiar → Proficient → Mastered** (4-level scale). "Mastered" requires correct answers in a verification task after a time delay.
- **Bayesian Knowledge Tracing (BKT)** — The probabilistic algorithm tracking per-competency mastery, updated per response. Stateless — see **AD-1**.
- **Knowledge Atom (ذرة معرفية)** — The smallest unit of remediation content. Typed: `AUDIO_VISUAL`, `SIMULATION`, `MIND_MAP`.
- **Heatmap (خريطة الحرارة)** — Students × competencies matrix; red = not mastered / yellow = partial / green = mastered.
- **Remediation Group (فوج المعالجة)** — Auto-formed cluster of students sharing a gap profile.
- **Pedagogical Alert (تنبيه بيداغوجي)** — Notification on persistent difficulty. Severity: `INFO`, `WARNING`, `CRITICAL`. Delivered via SSE — see **AD-5**.
- **Pillars** — Pedagogical dimensions: cognitive, affective, values, spiritual. V1 delivers cognitive/pedagogical only.
- **Year-band** — Algerian primary tier: Foundation (Y1–2), Transition (Y3), Consolidation (Y4–5).
- **Organization** — Tenant boundary entity. Every user and content item belongs to one organization. See **AD-4**.