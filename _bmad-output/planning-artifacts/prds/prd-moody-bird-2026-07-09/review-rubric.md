# PRD Quality Review — Ihsane Platform

## Overall verdict

This PRD has a genuine, non-swappable thesis — error-as-signal pedagogy routed to the smallest missed knowledge particle for Algerian primary education — carried by a coherent feature arc, strong counter-metrics, and honest brownfield ratification framing. It is at risk in two areas that matter most for a launch with real child users: **done-ness clarity** is thin (10 of ~33 FRs have no testable consequences, and several defined FRs carry undefined thresholds — "threshold response time," "spaced interval," "delayed verification"), and several **launch-critical open questions lack urgency signals** (child onboarding in OQ-2, pilot school selection in OQ-7). The glossary, UJ protagonists, and counter-metrics are genuinely strong; the FR consequences and NFR thresholds are where downstream stories will break.

---

## 1. Decision-readiness — adequate

A decision-maker can navigate the resolved/open landscape: OQ-1, OQ-3, OQ-6 are marked `✅ RESOLVED` with their resolution summarized inline (§8). The `[NOTE FOR PM]` tags sit at genuine tensions — FR-8a's AI guardrail gap, FR-27's underspecified alert thresholds, §6.2's admission that the affective engine is "the biggest vision-vs-reality gap." The addendum's A1 ("Rammed in the PRD as reality") on the Vue-vs-Flutter decision is admirably blunt about a trade-off that was already made.

Where it falters is urgency and launch-blocking risk. OQ-2 (how Year-1–2 pre-literate children are onboarded and rostered to a parent and class) is the operational prerequisite for putting real children on the platform, yet it carries only a soft `[ASSUMPTION: parent creates child accounts + PIN]` and no `[NOTE FOR PM]` flagging it as a launch blocker. OQ-7 (pilot school selection) is a single line — "1–2 Algerian schools" — with no selection criteria, no timeline, no owner. For a launch, these two OQs alone should be visibly escalated. The resolved OQs also don't record *who* decided, *when*, or what alternatives were weighed — fine for ratification, but it makes the decision audit trail thin if a stakeholder challenges the resolution later.

### Findings
- **high** — Launch-blocker OQs lack urgency signals (§8, OQ-2 & OQ-7) — Child onboarding and pilot school selection are the two items that gate actual children using the product, yet neither carries a `[NOTE FOR PM]` or a deadline. They read with the same weight as OQ-8 (perf targets). *Fix:* Tag OQ-2 and OQ-7 as `[LAUNCH-BLOCKER]` with owner + decision-by date; add `[NOTE FOR PM]` at OQ-2 explaining the operational dependency (no children on platform → no pilot data → no SM measurement).
- **medium** — Resolved OQs lack decision provenance (§8) — OQ-1/3/6 record *what* was decided but not *by whom, when, or what alternatives were rejected*. For a ratified PRD this is acceptable, but a stakeholder challenging the privacy regime or the AI-authoring flow has no trail. *Fix:* Add a one-line "Decided by [role], [date]; rejected alternative: [X]" to each resolved OQ.
- **low** — FR-8a cross-refs "See OQ on AI guardrails" vaguely (FR-8a, L175) — The actual reference is OQ-9, not named. *Fix:* Replace with "See OQ-9."

---

## 2. Substance over theater — adequate

The vision is the opposite of theater. "Error as a smart indicator for learning (مؤشر ذكي للتعلم)," routing to "the smallest knowledge particle," the Passport-as-verification-not-test, the concrete→abstract progression — none of this is swappable into another PRD. The personas carry genuine emotional and contextual JT layers (the Student's "feel safe making errors"; the Parent's "feel able to help even though I'm not a pedagogy specialist"; the Expert's "not buried in raw data"), and these JTs demonstrably drive FRs (FR-21's non-numeric insights exist *because* of the parent's emotional JT). The addendum's A4 is unflinching about shipping only 1 of 4 pillars.

NFR theater is where substance drops. §10 Reliability says "`GET /health` endpoint for monitoring; pilot-level availability (single-school, < 500 users)" — "pilot-level availability" is not a number; there is no uptime target, no degradation mode, no RPO/RTO. §10 Observability is literally an assumption placeholder: `[ASSUMPTION: deeper logging/metrics TBD]`. §10 Security lists mechanisms ("rate limiting on auth endpoints, CORS allow-list, CSP headers") without thresholds — what rate? what allow-list? These read as a checklist of things-implemented rather than properties-to-verify. For a launch handling children's data under Law 18-07, "rate limiting on auth endpoints" with no rate is a gap a reviewer can't accept or reject.

### Findings
- **high** — Reliability NFR is theater (§10, L448) — "Pilot-level availability" and a health endpoint do not constitute a reliability target. A launch with real users needs at least: target uptime (e.g., 99% during school hours), degradation behavior (read-only mode? cached content?), and incident-response expectation. *Fix:* Replace "pilot-level availability" with a concrete uptime target scoped to school-hours window; add a degradation-mode statement.
- **medium** — Observability NFR is a placeholder (§10, L449) — "Deeper logging/metrics TBD" means the PRD has no observability position. For pilot launch, you need at minimum: what's logged (auth events, error events, diagnostic-completion events), retention, and whether there's alerting. *Fix:* Define a minimum logging surface (auth, errors, session lifecycle) even if full metrics are deferred.
- **medium** — Security NFRs list mechanisms without thresholds (§10, L447) — "Rate limiting on auth endpoints" without a rate is unverifiable. *Fix:* Add the actual rate limit (e.g., 5 attempts/minute per IP on `/auth/login/*`) and define the CORS allow-list scope.
- **low** — FR-8a is arguably orthogonal to the pedagogical thesis (§4.2, FR-8a) — AI-assisted authoring is a content-loading operational feature, not a pedagogical-loop feature. It's fine to include it, but it slightly dilutes the "every feature serves the thesis" coherence. *Fix:* No action needed — just acknowledge it's an operational enabler, not a thesis-serving feature.

---

## 3. Strategic coherence — strong

There is a clear thesis and every feature serves it. The spine is: diagnose (FR-9–13) → classify error (FR-12) → remediate via smallest particle (FR-14–16) → verify via Passport (FR-17–19). Parent dashboard and expert analytics are decision-support surfaces orbiting the child's loop, not separate product lines. SM-1 (Gap Reduction Rate, ≥40%) directly validates the core thesis — if the diagnostic+remediation loop works, the gap shrinks. The counter-metrics are the best signal of strategic maturity in the document: SM-C1 ("raw time-on-platform must NOT be optimized; longer sessions may indicate frustration") and SM-C2 ("a rising score with flat Gap Reduction means the diagnostic is gaming itself") show the team has thought about how the metrics could be gamed and pre-empted it. The MVP scope kind is coherent — cognitive pillar only, explicitly stated and cross-referenced to the four-pillar model in addendum A4.

The weakness is that several success metrics don't yet have targets, which means the thesis can't actually be validated at pilot end. SM-2 ("target baseline to be set from first pilot cohort") is not a metric — it's a deferral. SM-4 ("students return within a week") has no percentage. SM-5 ("number of times a parent views the dashboard") has no number. A decision-maker reading §7 cannot answer "did the pilot succeed?" because three of five measurable SMs lack thresholds.

### Findings
- **high** — Primary/secondary SMs missing numeric targets (§7, SM-2/4/5) — SM-2 explicitly defers its target; SM-4 and SM-5 describe behavior without a pass/fail threshold. Without these, the pilot outcome is unjudgeable. *Fix:* Set minimum thresholds now (e.g., SM-4: ≥60% return within 7 days; SM-5: ≥1 dashboard view per alert). SM-2 can stay baseline-deferred but should define the *decision rule* (e.g., "if cohort median falls outside X range, trigger review").
- **medium** — SM-3 FR-validation link is weak (§7, SM-3 → FR-16/FR-18) — Retention ("solve a similar situation one week later") is almost entirely a spaced-re-surfacing claim (FR-16). FR-18 (Passport task) verifies mastery at end-of-pathway, not retention across time. The cross-ref inflates FR-18's role. *Fix:* Validate SM-3 against FR-16 primarily; note FR-18's contribution is indirect (mastery gating).
- **low** — "Integration situation" used in SM-3 without glossary definition (§7, SM-3) — This is a specific Algerian-curriculum term (per addendum A5: "extract data → choose operation → formulate answer"). Using it in a success metric without defining it creates downstream ambiguity. *Fix:* Add to glossary.

---

## 4. Done-ness clarity — thin

This is the dimension downstream stories lean on hardest, and it is the weakest part of the PRD. The problem is twofold: a large block of FRs have **no Consequences section at all**, and several FRs that *do* have consequences reference **undefined thresholds**.

FRs with no testable consequences (no "Consequences (testable)" block):
- **FR-6** (Manage question-bank items) — no consequences. What validates a well-formed item? Required fields? Distractor count?
- **FR-7** (Manage knowledge atoms) — no consequences. What's the atom data model? How is "attach to competencies" verified?
- **FR-15** (Deliver atoms concrete→abstract) — no consequences. "Present the concept a different way" is unmeasurable. How is concrete→abstract encoded? Is there a progression field?
- **FR-18** (Passport competency task) — no consequences. What defines pass/fail? How many items? What threshold? This is the mastery-gating event and it has no testable outcome.
- **FR-20** (Subject-strength radar) — no consequences. Which competencies aggregate into which radar axis? How many axes?
- **FR-22** (Daily reinforcement recommendation) — no consequences. What generates the recommendation? What data feeds it? What makes it "daily"?
- **FR-23** (Competency heatmap) — no consequences. What's the cell-coloring rule mapping mastery level to 🔴/🟡/🟢? The glossary defines the colors but not the thresholds.
- **FR-25** (Export reports PDF/CSV) — no consequences. What data is in the export? What granularity? Per-student? Per-class?
- **FR-26** (Printable remediation cards) — no consequences. What's on the card? Student name + gap + recommended atoms? Format?
- **FR-29** (Local content cache) — no consequences. What content is cached? Size budget? Eviction policy? "Brief connectivity drops" — how brief?

That is 10 of ~33 FRs — nearly a third — with no testable consequence. A story writer encountering FR-18 (Passport) has nothing to write an acceptance criterion from.

FRs with consequences but undefined thresholds or vague language:
- **FR-9**: "can resume if interrupted (offline-tolerant)" — the consequence only covers session creation (`POST /diagnostic/start`), not resume semantics. Resume from which item? How much client state?
- **FR-10**: "targets the learner's ZPD" — ZPD (Zone of Proximal Development) is not in the glossary and the consequence is unmeasurable as written.
- **FR-11**: "threshold response time" — what threshold? The entire difficulty-adjustment consequence depends on a number that isn't here.
- **FR-16**: "spaced interval" — what interval? The consequence says "not immediately re-drilled" but gives no actual spacing rule.
- **FR-17**: "delayed verification" — what delay? Cross-refs OQ-5, but the consequence is untestable until OQ-5 resolves.
- **FR-19**: "alert of appropriate severity" — "appropriate" is the vague word the rubric warns against.

### Findings
- **critical** — 10 FRs lack any testable consequences (FR-6, FR-7, FR-15, FR-18, FR-20, FR-22, FR-23, FR-25, FR-26, FR-29) — Downstream stories cannot be written from these FRs without invention. FR-18 (Passport pass/fail) and FR-15 (concrete→abstract encoding) are core-loop features with zero testable definition. *Fix:* Add a Consequences block to each, with at least one concrete, verifiable outcome (data shape, threshold, or observable behavior). Prioritize FR-18 and FR-15 — they gate the mastery loop.
- **high** — Undefined thresholds inside existing consequences (FR-9, FR-10, FR-11, FR-16, FR-17, FR-19) — "Threshold response time," "spaced interval," "delayed verification," and "appropriate severity" are all load-bearing phrases with no numbers. FR-11's entire behavior hinges on an unnamed threshold. *Fix:* Either inline the threshold (e.g., "correct answer in < P50 response time → difficulty up") or add `[THRESHOLD: TBD — see OQ-X]` with an explicit OQ cross-ref so the gap is tracked, not hidden.
- **medium** — "A different way" is unmeasurable (FR-15, L249) — "Present the concept a different way" is the core remediation promise and it's phrased as vibes. *Fix:* Define what "different way" means structurally (e.g., "atom carries a `modality` field: visual / manipulative / verbal; pathway must include ≥1 modality not used in the original item").
- **medium** — FR-9 resume semantics missing (FR-9, L206) — The FR says "can resume if interrupted" but the consequence only covers session start. *Fix:* Add a consequence for resume (e.g., "POST /diagnostic/resume with session_id returns the next unanswered item; partially-answered items are not re-scored").

---

## 5. Scope honesty — adequate

Scope honesty is genuinely strong on the explicit side. §5 (Non-Goals) is detailed and includes principled anti-goals — "remediation is not repetition," "no cutthroat competition; leaderboards rank most-improved, not top score." The `[ASSUMPTION]` tags are used inline at real inference points. The `[NOTE FOR PM]` at §6.2 for the affective engine ("a named differentiator currently unbuilt — the biggest vision-vs-reality gap") is exactly the kind of honest tension-flagging the rubric wants. The brownfield framing in §0 ("Ratification, not greenfield") sets honest expectations.

The honesty breaks in one structural way: §6.1 is headed "In Scope (v1 — built)" but the pre-literate rendering line (L379) says "backend ready, **frontend to build**." The section label claims the entire scope is built, but FR-8b and FR-8c are explicitly unbuilt — and they're marked "pilot-blocking for Y1–2." This is a scope-honesty contradiction: the pilot cohort is Year 1–2 (pre-literate), and the feature that makes the platform usable for them is admitted as not-yet-built inside a section labeled "built." For a launch, this is the single most important scope fact and the header obscures it.

The Assumptions Index roundtrip is broken (see Mechanical Notes), which undermines the honesty apparatus — two inline `[ASSUMPTION]`s are silently absent from the index, meaning a reviewer scanning §9 would believe they've seen all assumptions when they haven't.

### Findings
- **high** — §6.1 header "v1 — built" contradicts FR-8b/8c "frontend to build" (§6.1, L375 vs L379) — The pilot-blocking feature for the pilot cohort is labeled as part of "built" scope. A reader scanning headers gets a false signal. *Fix:* Either retitle §6.1 to "In Scope (v1)" and add a built/remaining column, or split into §6.1a (built) and §6.1b (remaining build: FR-8b, FR-8c). Flag with `[NOTE FOR PM: FR-8b/8c are the only unbuilt v1 items and they are pilot-blocking.]`
- **medium** — Assumptions Index roundtrip broken (§9 vs §10 L449, §11 L461) — Two inline `[ASSUMPTION]`s (observability logging, OVH EU region) are not indexed; one index entry (§6.2 affective engine) is actually a `[NOTE FOR PM]`, not an `[ASSUMPTION]`. The index is the honesty audit surface and it's incomplete. *Fix:* Add the two missing entries; reclassify or duplicate the §6.2 entry correctly. (See Mechanical Notes for detail.)
- **low** — OQ density acceptable but two are blockers (§8) — Six open OQs at launch stage is manageable, but OQ-2 and OQ-7 should be visually distinguished from OQ-8 (perf verification) and OQ-5 (algorithm tuning). *Fix:* Group OQs by impact: `[LAUNCH-BLOCKING]` vs `[TUNING]`.

---

## 6. Downstream usability — adequate

The glossary (§3) is a genuine strength: 16 terms, bilingual (AR/FR), with cardinality notes ("a module contains many competencies") and explicit scoping ("v1 delivers cognitive; affective + values layers are v2"). Domain nouns — Competency, Knowledge Atom, Remediation Pathway, Passport, Mastery Level, Pedagogical Alert — are used identically across FRs, UJs, and SMs. All four UJs have named protagonists (Maryam, Amine's mom, Mr. Karim, Ms. Lila) with entry state, path, climax, resolution. FR→UJ and SM→FR cross-references all resolve.

Two structural issues impede downstream usability. First, there are **two sections both numbered `### 4.3`** (L179 "Pre-Literate Item Rendering" and L199 "Adaptive Diagnostic Engine"). This cascades — every section number from 4.4 onward is off-by-one relative to a natural reading. Second, the FR numbering uses sub-letters (FR-8a, FR-8b, FR-8c) which §0 explicitly promised would not happen ("globally numbered FR-1…FR-N"). These resolve, but a downstream tool or story template parsing "FR-N" integers will stumble.

For a **brownfield** PRD specifically, the downstream usability gap is that UJs don't distinguish built flows from to-build flows. UJ-1 (Maryam) references "FR-9…FR-19" as realized, but FR-8b/8c (audio read-aloud, image-choice) — which Maryam as a pre-literate Year-2 student *depends on* — are to-build. A reader of UJ-1 cannot tell which parts of Maryam's journey work today and which require the FR-8b/8c build. The brownfield shape demands this distinction.

### Findings
- **high** — Duplicate `### 4.3` section headers (L179, L199) — Two different features share the same number. Every downstream section (4.4–4.10) is effectively misnumbered. *Fix:* Renumber: Pre-Literate Rendering stays 4.3, Adaptive Diagnostic becomes 4.4, cascade through 4.11.
- **medium** — UJs don't distinguish built vs to-build flows (§2.3, UJ-1) — UJ-1's protagonist is pre-literate and depends on FR-8b/8c (to build), but the UJ presents the journey as a unified narrative with no build-status marker. Brownfield downstream consumers need to know what's aspirational. *Fix:* Add a `[BUILD STATUS]` line per UJ (e.g., UJ-1: "Partial — FR-8b/8c rendering unbuilt; FR-9–19 built").
- **medium** — Glossary terms missing for "ZPD" and "integration situation" (FR-10 L215, SM-3 L406) — Both are used in testable consequences / success metrics but neither is in §3. "ZPD" drives the FR-10 consequence; "integration situation" drives SM-3. *Fix:* Add both to glossary with operational definitions.
- **low** — FR-8a/8b/8c sub-lettering breaks §0 numbering promise (§0 L17, §4.2–4.3) — §0 says "globally numbered FR-1…FR-N" but the actual scheme uses letter suffixes. *Fix:* Either renumber to FR-9, FR-10, FR-11 (and cascade) or amend §0 to say "FR-1…FR-N with letter-suffix sub-items where a feature extends a base FR."
- **low** — UJ-2 protagonist named by relation, not own name (§2.3, UJ-2) — "Amine's mom" vs Maryam / Mr. Karim / Ms. Lila. Minor inconsistency in protagonist-naming discipline. *Fix:* Give her a name (e.g., "Khadija, Amine's mother").

---

## 7. Shape fit — strong

The shape fits. This is a multi-stakeholder consumer product (Student / Parent / Expert), and UJs are load-bearing — present for all three roles, each with entry state → path → climax → resolution, each referencing FR ranges. None of the UJs are decorative; each one exercises a distinct feature cluster. The brownfield shape is handled well: the ratification framing (§0) is explicit, the addendum (A1, A2) absorbs inherited ADRs as constraints-not-decisions, and existing-code references are accurate (Valkey, Dexie/IndexedDB, Celery, FastAPI, Vue 3, `media_urls`, ADR-001–006, DEC-001–005). The PRD is not forced into a greenfield shape — it consistently says "the implementation already exists" and "backend ready, frontend to build" where appropriate.

The only shape-fit wrinkle is the §6.1 "built" label issue (covered under Scope Honesty): a brownfield PRD's value proposition is precise mapping of what-exists vs what-remains, and §6.1 blurs that by labeling unbuilt pilot-blocking work as "built." This is a shape-fit lapse specific to the brownfield context.

### Findings
- **medium** — Brownfield built/remaining mapping insufficient (§6.1) — A brownfield ratification PRD's distinctive value is the built-vs-remaining map. §6.1 presents a flat "built" list that includes unbuilt items. *Fix:* Add a "Build Status" annotation per scope item (Built / Partial / To-build), or split §6.1 into built vs remaining-build subsections.
- **low** — UJ build-status markers absent (§2.3) — See Downstream Usability finding; repeating here as a shape-fit note since brownfield UJs should flag which journeys are fully operational today. *Fix:* `[BUILD STATUS]` per UJ.

---

## Mechanical notes

- **Duplicate section numbering:** Two `### 4.3` headers exist — "Pre-Literate Item Rendering" (L179) and "Adaptive Diagnostic Engine" (L199). The second should be 4.4, cascading all subsequent sections (+1).

- **Assumptions Index roundtrip broken (3 defects):**
  1. §10 L449: `[ASSUMPTION: deeper logging/metrics TBD — not documented in sources.]` — **not in §9 index.**
  2. §11 L461: `[ASSUMPTION: OVH EU region — confirm in architecture.]` — **not in §9 index.**
  3. §9 index entry "§6.2 — Affective engine is the biggest vision-vs-reality gap" — but §6.2 L394 contains a `[NOTE FOR PM]`, **not** an `[ASSUMPTION]`. The tag type is mismatched. Either convert the §6.2 inline tag to `[ASSUMPTION]` or remove the index entry (the affective-engine gap is already surfaced via `[NOTE FOR PM]`).

- **Glossary drift (3 terms):**
  - "ZPD" — used in FR-10 consequence (L215); not in glossary.
  - "integration situation" — used in SM-3 (L406) and addendum A5; not in glossary despite being a load-bearing curriculum term.
  - "Pillars" count mismatch — §3 glossary (L103) defines **three** pillars (cognitive, affective, values); §1 vision (L21) also says three; but addendum A4 lists **four** (pedagogical, affective, spiritual, values). The PRD and addendum disagree on pillar cardinality. Reconcile: the glossary should match the canonical (four-pillar) model from the vision doc, or the addendum should note the PRD's three-pillar simplification explicitly.

- **FR numbering scheme:** §0 (L17) promises "globally numbered FR-1…FR-N." Actual scheme uses FR-8a, FR-8b, FR-8c sub-letters. These resolve but violate the stated convention.

- **§6.1 self-contradiction:** Header "In Scope (v1 — built)" (L375) vs line item "frontend to build" (L379) within the same section.

- **SM-3 FR cross-ref slightly inflated:** SM-3 validates FR-16 + FR-18, but retention is primarily FR-16 (spaced re-surfacing). FR-18 (Passport) verifies end-of-pathway mastery, not cross-time retention.

- **UJ protagonist naming:** 3 of 4 UJs use personal names (Maryam, Mr. Karim, Ms. Lila); UJ-2 uses "Amine's mom" (relation-based). Minor inconsistency.

- **Cross-reference integrity:** All UJ→FR ranges (UJ-1: FR-9…19; UJ-2: FR-20…22, FR-27; UJ-3: FR-23…26; UJ-4: FR-5…8) resolve. All SM→FR refs resolve. No broken cross-refs found.

- **`[NOTE FOR PM]` placement:** All four instances (FR-8a L175, FR-27 L328, §6.2 L392, §6.2 L394) sit at genuine tensions. No theatrical or redundant notes. Missing `[NOTE FOR PM]` at: OQ-2 (launch-blocking onboarding) and §6.1 FR-8b/8c line (pilot-blocking unbuilt work).
