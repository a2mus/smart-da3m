# Addendum — Ihsane Platform PRD

*Depth that belongs downstream (architecture, v2/v3 scope) or earned a place but didn't fit the PRD's main narrative. The PRD is the authoritative artifact; this file preserves context.*

## A1. Tech-stack decision — why Vue 3 (not Flutter)

The master-vision doc (`مشروع_المنصة_التعليمية.md`) proposes **Flutter + microservices** for the frontend. The shipped implementation (README, memory-bank, and the actual codebase) uses **Vue 3 PWA + FastAPI (modular monolith)**. This PRD ratifies **Vue 3** because:

- The implementation already exists and works (11 features merged, build passing, deployed).
- ADR-001 chose a **Vue 3 SPA** over SSR (interactive exercises, not SEO-critical; bundle < 200 KB).
- PWA gives offline + mobile-first without a native binary (matches pilot constraints).
- Flutter would require a ground-up rewrite with no demonstrated MVP benefit for the pilot cohort.

**Rammed in the PRD as reality.** The Flutter proposal is recorded here as a rejected alternative.

## A2. Architecture decisions already made (ADRs)

From `memory-bank/core/patterns.md` and `decisionLog.md` — these are *constraints the PRD inherits*, not decisions to remake:

| Decision | Choice |
|---|---|
| ADR-001 | Vue 3 SPA over SSR |
| ADR-002 | Hybrid offline (IndexedDB/Dexie cache + Background Sync); full offline-first → v2 |
| ADR-003 | 3-tier auth (student PIN, parent/expert email+password, JWT in Valkey) |
| ADR-004 | Valkey over Redis (license-avoidant, protocol-compatible) |
| ADR-005 | Feature-based folder organization |
| ADR-006 | RTL-first CSS via logical properties; `dir` toggled by vue-i18n locale |
| DEC-001 | Caddy-only edge (HTTPS + reverse proxy + static serving) |
| DEC-002 | Caddy automatic HTTPS (Let's Encrypt) |
| DEC-003 | Build-time container → static files to shared volume (no Node runtime in prod) |
| DEC-004 | DuckDNS subdomain `ihsan-dz.duckdns.org` for pilot |
| DEC-005 | GitHub Actions + SSH deploy (tests gate deploy) |

## A3. Deferred vision layers (v2/v3 detail)

The vision doc is far richer than the v1 MVP. These are captured here so they are not lost, but they are **out of v1 scope** (see PRD §6.2).

### v2 — Beta
- **Gamification system:** XP economy (watch +10 / solve +20 / first-try challenge +50), badge hierarchy (Brave Attempter → Error Hunter → Subject Expert → values badges), avatar customization unlocks, "positive leaderboard" (most-improved, not top-score), pedagogic store (XP → educational currency → tangible rewards), printable "Remediation Champion" certificate.
- **Zakat al-Ilm (peer solidarity):** top students tutor struggling peers via 30-sec voice tips ("بصمة النصح") and an Inspired Answers Bank; "Support"/"Spreader of Good" badges; solidarity charter. *Requires audio moderation (safety).*
- **AI tutor (المعلم الرفيق):** Socratic, Khanmigo-style chatbot — guides via questions, never gives the answer; personalized exercise generation from student interests; cross-curricular remediation windows; confidence self-rating.
- **Affective engine:** mood check on entry, frustration detection (error repetition + slowing speed → "reflection pause" / breathing / nature clip), empathetic avatar ("Little Sage" / الحكيم الصغير), "Hour of Tranquility."
- **Languages:** Tamazight + English.
- **Full offline-first PWA.**

### v3
- **Deep adaptive learning:** Random Forest / neural-net item selection replacing fixed paths.
- **Virtual Labs & AR:** interactive 3D shape assembly; AR via phone camera (loaf, scale on the real table).
- **Gamification 2.0:** storytelling layer ("mission to save the city of knowledge"); live national challenges between students (Oran, Tamanrasset, Setif).
- **Native iOS/Android apps.**

### Non-goals (permanent)
- Live human tutoring; voice recognition/ASR; school/MoE replacement.

## A4. Four pedagogical pillars (vision context)

The master vision frames four strategic pillars. v1 ships pillar 1 only; pillars 2–4 are v2:

1. **Pedagogical (بيداغوجي)** — ✅ v1. Automated error diagnosis + individualized concrete→abstract remediation.
2. **Affective (وجداني)** — ⏳ v2. Frustration detection, calming interventions, empathetic avatar.
3. **Spiritual (روحي)** — ⏳ v2. Knight-Learner Charter, intention renewal, "Ihsane" excellence ethic.
4. **Values (قيمي)** — ⏳ v2. Zakat al-Ilm peer tutoring, role-model stories, process-oriented praise.

## A5. Algerian primary curriculum mapping (vision context)

The vision maps the primary tier into three pedagogical stages — relevant to content authoring (§4.2) and the chosen pilot scope (Y1–2):

| Stage | Years | Character | Platform implication |
|---|---|---|---|
| Foundation (تأسيس) | Y1–2 | Audio-dominant, phonological awareness, foundational arithmetic | Items must support audio-read questions + image choice (pre-literate). **Pilot scope.** |
| Transition (تحول) | Y3 | French introduced + math transformations | Bilingual content begins. |
| Consolidation (تثبيت) | Y4–5 | Methodological remediation of the integration situation (extract data → choose operation → formulate answer) | Complex item types; integration situations. |

*Pilot launch content = Year 1 & 2, Arabic + Math (per Mus). This overrides an earlier memory-bank note referencing Math Y4–5.*

## A6. Visual identity (vision context)

- Palette: olive/emerald green (Algerian identity, eye-comfort), white (clarity), calm gold (badges/Zakat).
- Typography: Arabic — Tajawal, Cairo; Latin — Plus Jakarta Sans.
- Simplified Algerian geometric ornaments.
- Implemented as a semantic color scale (no hardcoded colors — enforced by lint).
