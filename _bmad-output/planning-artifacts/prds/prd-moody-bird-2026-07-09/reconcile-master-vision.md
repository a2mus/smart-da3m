# Reconciliation: Master Vision (Arabic) → PRD + Addendum

**Source:** `مشروع_المنصة_التعليمية.md` (master vision, 738 lines, Arabic)
**Reconciled against:** `prd.md` (474 lines) + `addendum.md` (81 lines)
**Method:** Full read of source, then PRD + addendum. Gaps = ideas/requirements/tone/detail present in source but dropped, lost, or silently altered in the PRD. Aspirational v2/v3 items (affective engine, gamification, Zakat al-Ilm, AI tutor, AR, deep adaptive) that are *cleanly deferred* are NOT flagged — only genuinely-lost or mishandled content is.

---

## Summary verdict

The PRD + addendum capture the **structural skeleton** of the vision faithfully: the diagnostic→remediation→Passport loop, error classification, micro-tagging/knowledge atoms, 4-level mastery, heatmap + auto-grouping, parent radar + plain-language insights, bilingual RTL, visual identity, four pillars, curriculum mapping, and the v2/v3 deferrals. The addendum does heavy lifting preserving vision context (A3–A6).

What is lost is mostly **qualitative**: the pedagogical *philosophy* behind the atoms, the *tone* of error-handling, the child's *own voice* in metrics, and a few specific **v1-level remediation features** (explanatory feedback, graduated hints, virtual manipulatives as a content type) that are neither in FRs nor explicitly deferred — they fall through the crack between "cognitive core (v1)" and "affective layer (v2)."

---

## GAPS — Qualitative / Pedagogical Philosophy

### G1. "Pedagogy of Meaning" (بيداغوجيا المعنى) — the *why* before the *what*
**Source (§Affective Engine, lines 323–329):** Remediation must begin with "لماذا نتعلم هذا؟" — fractions taught as justice/sharing (تقسيم الطعام، الميراث المعنوي), language as spiritual/personal expression. The concept is anchored before the math.
**PRD:** FR-15 says only "concrete → abstract." The *meaning-first* framing — that an atom should connect the concept to the child's world and identity before drilling the mechanism — is absent.
**Why it's a gap, not a clean deferral:** The full affective engine is rightly v2, but "teach fractions through sharing bread" is a **v1 content-authoring principle** (how Ms. Lila should author atoms in FR-7/FR-8a). It is neither required by any FR nor named in the addendum's content-authoring guidance. It has silently collapsed into "values layer = v2."
**Suggested fix:** Add a content-quality NFR or an FR-7 consequence: knowledge atoms should open with a real-world/meaning anchor before the mechanism.

### G2. Tone & voice spec for child-facing error feedback
**Source (lines 334–337, 379):** Errors must **never** appear as a stark red ✗. The mandated voice is warm and destigmatizing — "لا بأس يا بطل، العظماء أخطأوا ليتعلموا" — and the avatar leads with reassurance, not correction.
**PRD:** No FR or NFR specifies the *tone* of error/feedback copy. UJ-1 mentions "immediate feedback on why each step matters" narratively, but nothing constrains the *affective register* of that feedback in v1.
**Why it's a gap:** The empathetic-avatar *machinery* is v2, but the **copy/tone principle** (never a bare red mark; always encouraging, non-stigmatizing language) is a v1 content/UX requirement that ships the moment any child sees a wrong answer. It is lost between "cognitive core" and "affective engine."
**Suggested fix:** Add a tone NFR under §10 or a content-guidance clause: all error feedback copy must be encouraging and never reduce to a stark ✗/red mark.

### G3. "Radical simplicity for the child" — algorithms silent behind the curtain
**Source (closing expert advice, lines 738):** "القوة الحقيقية ليست في كثرة الإضافات، بل في 'سلاسة التجربة'. يجب أن تبدو المنصة بسيطة جداً للطفل، بينما تختبئ كل هذه الخوارزميات المعقدة خلف الستار لتخدمه بصمت." — the child-facing surface must feel dead-simple while BKT/adaptive logic hides silently.
**PRD:** No UX/design principle captures this "complexity-hiding" mandate. The FRs describe the complex machinery (BKT, adaptive selection, error classification) without stating the corresponding child-surface simplicity obligation.
**Suggested fix:** Add to §10 NFRs or §11 guardrails: "the student surface must hide all pedagogical-engine complexity; no BKT/mastery/error-class jargon reaches the child."

---

## GAPS — Specific v1 Requirements Silently Dropped

### G4. Immediate explanatory feedback on *why* an error occurred
**Source (§3 remediation strategies table, line 40):** "التغذية الراجعة (Feedback): تقديم شروحات فورية عند كل خطأ لشرح 'لماذا هذا الخطأ؟'" — one of the **four core v1 remediation strategies**, alongside micro-videos, spaced repetition, and peer learning.
**PRD:** No FR requires per-error explanatory feedback. FR-13 only *records* the answer + response time; FR-15 delivers atoms; FR-19 badges. The "explain why this answer is wrong, immediately" requirement has no home.
**Why it's a gap:** This is listed in the source's general (non-affective, non-v2) remediation strategies. It is neither explicitly deferred nor implemented as an FR. It fell through the crack.
**Suggested fix:** Add an FR (e.g., FR-15a): on any incorrect response, the system surfaces an immediate explanation of *why* the answer is wrong (distinct from re-teaching the atom).

### G5. Graduated hints (تلميحات) during practice
**Source (Khan Academy model, lines 607, 657):** "تلميحات (Hints) تدريجية لا تعطي الإجابة مباشرة بل تشرح الخطوات المنطقية" — gradual hints that explain reasoning steps without giving the answer. Endorsed as core to the mastery loop the platform explicitly adopts ("Khan-Academy-influenced").
**PRD:** The PRD claims the mastery model is "Khan-Academy-influenced" (Glossary) but drops the **hint** feature entirely. No FR for graduated hints during diagnostic or practice.
**Why it's a gap:** Hints are v1-appropriate (no AI required — pre-authored hints on items). The platform claims the Khan lineage but omits the signature feature.
**Suggested fix:** Consider an FR for graduated, authorable hints on practice items; or explicitly defer with rationale.

### G6. Virtual manipulatives as a distinct content/interaction type
**Source (§primary remediation pathways, lines 110–114, 160–162, 180–181):** Remediation uses specific interactive manipulatives — digital cubes/coins for math, pizza-slicing, the "balance scale" (الميزان) for nominal sentences, drag-and-drop word sorting, coloring fractions. The pedagogy is "المحسوس قبل المجرد" — the *concrete* is literally a manipulable object.
**PRD:** FR-7 (knowledge atoms) and FR-8c (image_choice) treat content generically. The PRD supports `multiple_choice`, `image_choice`, `numeric` item types — but **no interactive-manipulative item type** (drag-and-drop, virtual object manipulation). Yet the two flagship worked examples (fractions, nominal sentence) *depend* on manipulatives.
**Why it's a gap:** The pilot-cohort pedagogy is manipulative-heavy, but the v1 item-type model can't express it. Either the pilot must drop its flagship interactions, or this is an undocumented scope cut.
**Suggested fix:** Either add a manipulative/interactive item type to v1, or explicitly document that pilot remediation will use video + choice only (and flag the pedagogical downgrade).

---

## GAPS — Metrics (child's own voice lost)

### G7. Child-facing satisfaction signal (emoji NPS / "معدل الابتسامة الرقمي")
**Source (§KPIs, line 488):** "معدل الابتسامة الرقمي (NPS): تقييم التلميذ للأفاتار والمنصة من خلال أيقونات تعبيرية بسيطة" — the child rates the platform via simple emoji.
**PRD Success Metrics:** SM-4 (student return-rate), SM-5 (parent engagement), SM-6 (accessibility). **No child-self-reported satisfaction signal.** All student signal is behavioral (return-rate), none is the child's *own voice*.
**Why it's a gap:** Emoji-NPS is v1-trivial (no affective engine needed) and is the only way a pre-literate child can express satisfaction. Dropped without rationale.
**Suggested fix:** Add an SM for child satisfaction via emoji rating.

### G8. Resilience Score (مؤشر الصمود)
**Source (§KPIs, line 478):** "مؤشر الصمود (Resilience Score): عدد المحاولات التي يقوم بها التلميذ قبل طلب المساعدة أو الخروج" — number of attempts before requesting help or exiting.
**PRD:** Not present. SM-C1 treats time-on-platform as a counter-metric, but the *attempt-count-before-exit* signal (a v1-measurable engagement/resilience proxy) is absent.
**Why it's a gap:** v1-measurable, behaviorally captured (already in the answer-event stream), and pedagogically meaningful. Lost in the metrics translation.
**Suggested fix:** Add an SM for resilience (median attempts before exit/help-request).

### G9. Effort-vs-Results ratio (مؤشر الجهد vs النتائج) — lost nuance
**Source (§technical engines, line 250):** "مؤشر الجهد vs النتائج: قياس الوقت الذي يقضيه التلميذ في المعالجة مقابل التحسن الفعلي" — a **ratio** of remediation time to actual improvement (efficiency).
**PRD:** SM-C1 folds *all* time-on-platform into a counter-metric ("must NOT be optimized"). The source's concept is an *efficiency ratio* (time ÷ improvement), which is a diagnostic signal, not raw engagement. The nuance — that time is only meaningful relative to the improvement it produces — is lost.
**Why it's a gap:** Not a contradiction (counter-metric is defensible) but a *loss of nuance*: the source wants to measure remediation *efficiency*, the PRD only says "don't optimize raw time."
**Suggested fix:** Consider an SM for remediation efficiency (improvement per unit time) as a diagnostic, even while raw time stays a counter-metric.

---

## GAPS — Minor / Weaker

### G10. Growth Mindset (عقلية النمو) not named as a v1 design principle
**Source (line 272):** Explicitly names "Growth Mindset" — reward *attempt and improvement* over *perfect score*.
**PRD:** Implicit in the mastery model (Attempted→Mastered) and in the deferred "most-improved" leaderboard, but never stated as a v1 design philosophy that should shape, e.g., badge/feedback copy or what the parent insight emphasizes.
**Severity:** Low — implicitly present; flagging only because the source names it explicitly as a guiding philosophy.

### G11. Quality Matters (QM) + special-needs pedagogical scope beyond WCAG
**Source (lines 733):** QM standards for accessibility *including children with reading or vision difficulties* (ذوي الاحتياجات الخاصة)، plus SCORM/xAPI portability.
**PRD:** WCAG 2.1 AA in v1; QM and SCORM/xAPI deferred to v2+ (§11). The specific *special-needs pedagogical* consideration (beyond technical accessibility) is not carried.
**Severity:** Low — WCAG AA covers much of it; QM deferral is reasonable. Flagging only the lost "special-needs pedagogy" framing.

### G12. "Error Log" (سجل الأخطاء) as a distinct per-student artifact
**Source (line 249):** "سجل الأخطاء: أرشفة الأخطاء المتكررة لكل تلميذ لتحليل 'سلوك التعلم' لديه" — a persistent per-student error archive for learning-behavior analysis.
**PRD:** Likely subsumed by BKT mastery tracking + analytics, but not named as a distinct, reviewable per-student error-history artifact.
**Severity:** Low — probably covered implicitly; flagging for explicitness.

### G13. Process-oriented praise / "كفاحي المثمر" reflection log
**Source (lines 358–362):** A student-facing log showing "how I was vs how I became through my patience" — process-oriented praise building self-confidence.
**PRD:** No student-facing reflection/progress-narrative surface. Sits in the Affective Engine section (arguably v2).
**Severity:** Low-borderline — could be argued v2; but a simple "my progress" narrative is v1-feasible and absent.

---

## Things checked and NOT gaps (confirmed correctly handled)

- v2 deferrals (gamification, Zakat al-Ilm, AI tutor, affective engine, deep adaptive, AR, gamification 2.0, native apps, Tamazight/EN) — cleanly deferred with rationale; addendum A3 preserves detail. ✅
- Four pillars — addendum A4. ✅
- Visual identity (olive/emerald, white, gold; Tajawal/Cairo; ornaments) — addendum A6. ✅
- Curriculum mapping (Foundation/Transition/Consolidation; pilot = Y1–2) — addendum A5. ✅
- Vue 3 vs Flutter decision — addendum A1. ✅
- ADRs inherited as constraints — addendum A2. ✅
- Error classification (3-way + rule-vs-mechanism) — Glossary + FR-12. ✅
- Micro-tagging / knowledge atoms — Glossary + FR-7, FR-14. ✅
- Dynamic difficulty — FR-11. ✅
- Mastery 4-level + delayed Mastered — Glossary + FR-17. ✅
- Heatmap + auto-grouping + remediation cards + export — FR-23…FR-26. ✅
- Parent radar + plain-language insights + daily recommendation — FR-20…FR-22. ✅
- Non-numeric reporting ("use performance verbs, not 6/10") — FR-21. ✅
- Passport → badge / fail → alert + in-person support plan — FR-19. ✅
- "Most improved" not "top score" (no cutthroat competition) — Non-Goals + SM. ✅
- Counter-metrics (raw time, raw score inflation) — SM-C1, SM-C2. ✅
- Pre-literate rendering (audio + image-choice) — FR-8b, FR-8c. ✅
- Bilingual AR/FR RTL — FR-28. ✅
- Privacy (Law 18-07 + GDPR-K) — §11. ✅
- Applied fractions scenario — reflected in UJ-1 + addendum examples. ✅

---

## Recommended actions (priority order)

1. **G4** (explanatory feedback) — strongest gap; v1 remediation strategy with no FR home. Add an FR.
2. **G2** (tone spec) + **G3** (radical simplicity) — add tone/simplicity NFRs to §10; these shape all child-facing copy and UX.
3. **G5** (graduated hints) + **G6** (virtual manipulatives) — decide explicitly: build in v1, or document the pedagogical downgrade. Currently ambiguous.
4. **G7** (child emoji-NPS) + **G8** (resilience metric) — cheap, v1-feasible, and they restore the child's own voice to the metrics.
5. **G1** (Pedagogy of Meaning) — add a content-authoring principle so FR-7/FR-8a atoms carry real-world meaning anchors.
6. **G9** (effort-vs-results) — refine SM-C1 into an efficiency ratio.
7. **G10–G13** — low priority; consider for completeness.
