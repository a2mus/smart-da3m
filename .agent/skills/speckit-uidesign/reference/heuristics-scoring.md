# Heuristics Scoring Reference

Score each of Nielsen's 10 Usability Heuristics 0–4. A 4 = genuinely excellent.

## 1. Visibility of System Status
Loading indicators, action confirmation, progress, current location, inline validation.
- 0: No feedback  1: Rare  2: Partial  3: Good (minor gaps)  4: Every action confirms

## 2. Match System / Real World
Familiar terminology, logical order, recognizable icons, domain language, natural reading flow.
- 0: Pure jargon  1: Mostly confusing  2: Mixed  3: Mostly natural  4: User's language throughout

## 3. User Control and Freedom
Undo/redo, cancel, navigation back, clear filters, escape multi-step.
- 0: Trapped  1: Obscure exits  2: Main flows have escape  3: Good control  4: Full control everywhere

## 4. Consistency and Standards
Terminology, same actions=same results, platform conventions, visual consistency.
- 0: Feels like different products  1: Many inconsistencies  2: Partially  3: Mostly  4: Fully cohesive

## 5. Error Prevention
Confirmation before destructive, constraints (date pickers), smart defaults, clear labels, autosave.
- 0: No guardrails  1: Few safeguards  2: Common errors caught  3: Most blocked  4: Nearly impossible

## 6. Recognition Rather Than Recall
Visible options, contextual help, recent items, autocomplete, labels on icons.
- 0: Heavy memorization  1: Mostly recall  2: Some aids  3: Good  4: Everything discoverable

## 7. Flexibility and Efficiency
Keyboard shortcuts, customizable, recent/favorites, bulk actions, power features.
- 0: One rigid path  1: Limited  2: Some shortcuts  3: Good accelerators  4: Highly flexible

## 8. Aesthetic and Minimalist Design
Only necessary info, clear hierarchy, purposeful color, no clutter, focused layouts.
- 0: Overwhelming  1: Cluttered  2: Some clutter  3: Mostly clean  4: Every element earns its pixel

## 9. Error Recovery
Plain language, specific identification, actionable suggestions, near source, non-blocking.
- 0: Cryptic codes  1: Vague  2: Clear but unhelpful  3: Clear with suggestions  4: Perfect recovery

## 10. Help and Documentation
Searchable help, contextual tooltips, task-focused, concise, accessible without leaving context.
- 0: None  1: Hard to find  2: Basic  3: Good searchable docs  4: Right info at right moment

---

## Rating Bands
| Range | Rating | Meaning |
|-------|--------|---------|
| 36-40 | Excellent | Minor polish — ship it |
| 28-35 | Good | Address weak areas |
| 20-27 | Acceptable | Significant improvements needed |
| 12-19 | Poor | Major UX overhaul required |
| 0-11 | Critical | Redesign needed |

## Issue Severity

| Priority | Name | Action |
|----------|------|--------|
| P0 | Blocking | Fix immediately — showstopper |
| P1 | Major | Fix before release |
| P2 | Minor | Fix in next pass |
| P3 | Polish | Fix if time permits |
