# Reconciliation: memory-bank/ ↔ PRD + Addendum

**Source under review:** All files under `memory-bank/` (8 files in `memory-bank/core/`: `projectBrief.md`, `productContext.md`, `techContext.md`, `patterns.md`, `decisionLog.md`, `progress.md`, `current-state.md`, `next-session.md`).
**PRD:** `prd.md` (draft, 2026-07-09). **Addendum:** `addendum.md`.
**Mode:** Brownfield ratification. The PRD ratifies a shipped MVP.
**Verdict:** The PRD is broadly faithful to the ADRs/DECs and the deferred-items list. It is **less faithful** to the *implemented-features* record in `progress.md`/`current-state.md`, where it over-claims at least two v1 capabilities and inherits two internal memory-bank contradictions without flagging them. Severity ratings: 🔴 blocking misrepresentation · 🟡 material omission · 🟢 minor/stale.

---

## 1. Over-claimed as built (PRD §6.1 "In Scope (v1 — built)")

### G1 — 🔴 FR-8a (AI-assisted content drafting) is presented as built, but memory-bank has no record of it being implemented.
- PRD §6.1 l.378 lists "Content management / expert back-office, **incl. AI-assisted drafting** — FR-5…FR-8a" under the v1-built scope, with no caveat.
- FR-8a (l.169–177) describes a *persistent* AI authoring aid that drafts items/atoms from a curriculum reference, with `DRAFT` gating and expert review.
- Neither `progress.md` (Key Features Implemented, l.62–88) nor `current-state.md` (Technical Achievements, l.63–71) mention any AI-assisted authoring capability. The implemented back-office covers modules / questions / atoms / bulk import only.
- The PRD itself is internally inconsistent: OQ-6 (l.429) and OQ-9 (l.432) treat AI-assisted authoring as a *live, unresolved* concern (guardrails, LLM provider, data residency). A feature with open guardrail/provider questions is not a shipped feature.
- **Fix:** Either move FR-8a to a "v1.1 / pilot-onboarding build" scope (mirroring the honest "backend ready, frontend to build" caveat used for FR-8b/FR-8c on l.379), or label §6.1 "v1 — built + ratification in-flight". As written, §6.1 over-claims.

### G2 — 🟡 FR-8b/FR-8c (pre-literate rendering) caveat is correctly applied, but FR-8a is not given the same treatment — inconsistent caveat policy.
- PRD §6.1 l.379 honestly annotates FR-8b/FR-8c: "*pilot-blocking for Y1–2; backend ready, frontend to build*".
- The same honesty is not extended to FR-8a (also unbuilt per memory-bank). The asymmetry suggests FR-8a was added later (OQ-9 is literally tagged "new") without re-grading §6.1.
- **Fix:** Apply a uniform "built / not-yet-built" tag to every row in §6.1.

### G3 — 🟡 FR-16 (spaced re-surfacing of errors) is listed as v1-built; memory-bank's implemented-feature list does not confirm it.
- PRD §6.1 l.381 includes "Remediation pathways + spaced re-surfacing — FR-14…FR-16" as built.
- `progress.md` backend achievements (l.64–74) enumerate "Remediation pathway generation" and "Passport assessment evaluation" but do **not** list spaced repetition / spaced re-surfacing / a spacing scheduler.
- `current-state.md` likewise mentions pathway + Passport but not spacing.
- This is plausibly implemented and under-documented, but for a brownfield ratification the PRD should not assert a capability the memory-bank doesn't corroborate. **Recommend:** either cite the implementing module or mark FR-16 as "to verify".

### G4 — 🟢 FR-19 competency badge vs. memory-bank "badges → v2" deferral — latent ambiguity.
- PRD FR-19 (l.273) and Glossary (l.97) introduce a **v1 competency badge** earned on Passport pass, gating advancement.
- `progress.md` Deferred Items l.98 defers "Gamification system (XP, **badges**, avatar) → Beta v2".
- The PRD's glossary distinguishes a *competency badge* (mastery gate) from *gamification badges* (reward/affective), so the two are reconcilable — but the PRD never addresses the tension with the memory-bank's blanket "badges" deferral. A one-line note in §6.2 ("competency badge ≠ gamification badges") would close it.

---

## 2. Internal memory-bank contradictions the PRD inherits without flagging

### G5 — 🔴/🟡 "Full offline support" contradiction between `current-state.md` and ADR-002 / `progress.md`.
- `current-state.md` l.68 lists "**Full offline support** via Dexie.js IndexedDB" as a completed Technical Achievement.
- ADR-002 (`patterns.md` l.6): "Hybrid offline strategy … **Full PWA offline deferred to v2**."
- `progress.md` Deferred Items l.101: "PWA offline mode → Beta v2".
- `productContext.md` l.43: "Offline-capable content caching (Workbox + Dexie.js) — **full offline deferred to v2**".
- The PRD §4.10 / §6.2 correctly adopts the ADR-002 framing ("foundation built, full offline-first = v2"). But it does so silently — it ratifies the ADR and ignores the contradictory `current-state.md` achievement claim. A reconciling PRD should **explicitly note** that `current-state.md`'s "full offline support" line overstates v1 scope, so downstream readers know which source to trust. As written, a reader cross-checking the PRD against `current-state.md` will see a discrepancy the PRD doesn't acknowledge.

### G6 — 🟡 `techContext.md` dev stack references **Nginx**, contradicting DEC-001 (Caddy-only).
- `techContext.md` l.31: "Dev: Docker Compose stack (FastAPI + PostgreSQL + Valkey + Celery + **Nginx**)".
- DEC-001 (`decisionLog.md` l.15–68) explicitly *rejected* Nginx in favour of Caddy-only; `current-state.md` l.73 confirms "Caddy-only architecture".
- The PRD addendum A2 (l.28) correctly records "DEC-001 | Caddy-only edge". So the PRD is right and `techContext.md` l.31 is stale — but the PRD inherits the staleness silently. Recommend the reconciliation note flag `techContext.md` l.31 as superseded by DEC-001 so the architecture agents don't re-introduce Nginx.

---

## 3. Privacy / residency gap (CDN omitted)

### G7 — 🟡 PRD §11 privacy story omits **Cloudflare CDN**, which `techContext.md` places in front of OVH.
- `techContext.md` l.18: "CDN | Cloudflare Free | — | SSL, DDoS, caching"; l.32: "Prod: Single OVH VPS, Docker Compose, **Cloudflare CDN in front**".
- PRD §11 l.455–462 grounds its child-data privacy regime in "Data hosted on OVH (EU region)" under Algerian Law 18-07 + GDPR-K. It never mentions Cloudflare.
- If Cloudflare terminates TLS (the standard free-tier topology), child-attributable traffic transits a non-EU (US-headquartered) party before reaching OVH. That is *directly material* to the §11 residency/consent analysis and to OQ-9's LLM-provider residency question.
- There is also a secondary internal contradiction: DEC-002 (`decisionLog.md` l.122–128) assigns SSL termination to **Caddy via Let's Encrypt automatic HTTPS**, which conflicts with a Cloudflare-in-front topology (where Cloudflare terminates the edge cert and Caddy only sees Cloudflare's origin pull). The PRD addendum A2 lists DEC-002 as accepted without reconciling it with Cloudflare.
- **Fix:** Either (a) confirm Cloudflare is *not* in the pilot path and update `techContext.md`, or (b) add a row to PRD §11 / a new OQ covering CDN TLS termination and its residency impact under 18-07.

---

## 4. Under-represented infrastructure (Spec 003 / design-quality enforcement)

### G8 — 🟡 PRD captures the WCAG *outcome* but not the design-quality *enforcement machinery* recorded in memory-bank.
- Memory-bank documents a whole completed spec — "Spec 003 — Design Quality Enforcement", 39/39 tasks (`current-state.md` l.23–30, `progress.md` l.48–60, `next-session.md` l.11–36): Husky + lint-staged pre-commit hooks, Stylelint + ESLint rules enforcing color-token + logical-CSS constraints, retroactive color remediation, RTL/LTR logical-CSS migration, axe-core WCAG AA audit (6 routes, 0 violations), semantic color scale documented in `frontend/README.md`, and a `design-lint` CI job that **gates** `test` + `deploy` in `.github/workflows/deploy.yml`.
- PRD §10 l.450 mentions only the audit outcome ("WCAG 2.1 AA, 0 violations on audited routes"). Addendum A6 l.81 adds "enforced by lint" in one clause.
- For a brownfield ratification, the *enforcement layer* (pre-commit + CI gate) is a real architectural commitment that downstream agents should inherit. The PRD under-states it. **Recommend:** a one-line NFR in §10 — "RTL-hard-rule and semantic-color-scale are enforced via pre-commit (Husky/lint-staged) and a `design-lint` CI gate that blocks deploy" — so it isn't lost.

---

## 5. Design decisions recorded in memory-bank but absent from the PRD

### G9 — 🟢 "Three visual interface variants by age band (6–7, 8–9, 10–11)" (`productContext.md` l.13) is not reflected in the PRD.
- The PRD's age-band discussion (§3 "Year-band", addendum A5) is purely about *content/pilot scope*, not about distinct UI variants per age band. Whether the three-variant design is actually built is unclear from memory-bank (no corroboration in `progress.md`), but it is a recorded product decision the PRD neither ratifies nor rejects.

### G10 — 🟢 Touch-target / audio-feedback specifics from `productContext.md` are dropped.
- `productContext.md` l.40: "Touch targets minimum 60px for student-facing elements"; l.41: "Audio support for ages 6–8 instructions **and feedback**".
- PRD FR-8b covers audio read-aloud of *question text* but not *feedback* audio; no touch-target minimum appears in the PRD's NFRs. Minor, but these are testable child-UX constraints the PRD silently narrows.

### G11 — 🟢 Adaptive-engine implementation detail (scikit-learn + multi-arm bandit) omitted.
- `techContext.md` l.12 records the adaptive engine as "scikit-learn + custom BKT … multi-arm bandit". PRD FR-10/FR-11 describe BKT-driven selection and dynamic difficulty abstractly, without naming the bandit. Not a misrepresentation, but architecture agents downstream will need this; the PRD is the natural place to pin it.

---

## 6. Correctly represented (no gap)

For completeness, these memory-bank positions are faithfully carried into the PRD/addendum and need no action:

- **All six ADRs** (`patterns.md`) and **all five DECs** (`decisionLog.md`) are accurately transcribed in addendum A2 (l.20–32). Spot-checked ADR-001/002/003/004/005/006 and DEC-001/002/003/004/005 — all faithful.
- **11 feature branches merged, deployed to `ihsan-dz.duckdns.org`** (PRD §0 l.15) matches `current-state.md` l.10, l.77 and `next-session.md` l.7.
- **Three-tier auth** (PIN / email-password / JWT-in-Valkey) — PRD §4.1 matches ADR-003 and `productContext.md` l.12/19/24.
- **Deferred items list** — PRD §6.2 (gamification, Zakat al-Ilm, AI tutor, affective engine → v2; deep ML, virtual labs/AR, native apps → v3) is consistent with `progress.md` l.97–105 and `projectBrief.md` Non-Goals. The affective-engine gap is correctly flagged as "the biggest vision-vs-reality gap" (PRD §9, §6.2).
- **Non-goals** (no live tutoring, no ASR, no school replacement, primary-tier only) — PRD §5 matches `projectBrief.md` l.14–20.
- **Bundle < 200 KB, < 3 s on 3G, < 200 ms API P95** — PRD §10 l.446 matches `techContext.md` l.7 and `productContext.md` l.39; PRD honestly marks these unverified (OQ-8), consistent with `next-session.md` l.60.
- **WCAG 2.1 AA, 6 routes, 0 violations** — PRD §10 l.450 matches `next-session.md` l.20.
- **Success metrics** (≥ 40 % gap reduction, ≥ 70 % 1-week retention, ≥ 60 % weekly parent engagement, ≤ 30 % abandonment, ≥ 99.5 % uptime) — PRD §7 matches `projectBrief.md` l.22–27.
- **Pilot scope = Y1–2 Arabic + Math** — addendum A5 l.74 explicitly overrides the older `current-state.md` l.37 / `next-session.md` l.46 reference to "Mathematics السنة 4 & 5". The override is correctly noted.

---

## 7. Recommended PRD edits (priority order)

1. **G1/G2** — Re-tag FR-8a as not-yet-built (or "v1.1") in §6.1; apply a uniform built/not-built caveat column to §6.1. *(blocking for a ratification claim)*
2. **G7** — Add a CDN/residency row to §11 or a new OQ; reconcile DEC-002 SSL termination vs. Cloudflare-in-front. *(material for the child-data privacy claim)*
3. **G5** — Add an explicit note that `current-state.md`'s "full offline support" line overstates v1; the PRD ratifies ADR-002 (foundation only). *(prevents downstream confusion)*
4. **G3** — Either cite the implementing module for FR-16 or mark it "to verify".
5. **G8** — Add one NFR line capturing the pre-commit + `design-lint` CI gate so the enforcement layer is inherited.
6. **G6** — Note that `techContext.md` l.31 (Nginx in dev) is stale vs. DEC-001.
7. **G4/G9/G10/G11** — Minor: add the competency-badge clarification, three-variant-by-age-band decision status, touch-target/audio-feedback NFRs, and the scikit-learn/bandit implementation note.

---

*Reconciliation target: `/memory-bank/` (8 files). Author: reconciliation subagent. Date: 2026-07-11.*
