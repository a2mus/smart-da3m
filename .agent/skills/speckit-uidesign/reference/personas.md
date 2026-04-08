# Personas Reference

Select 2-3 personas most relevant to the interface. Walk through the primary action. Report specific red flags.

---

## 1. Impatient Power User — "Alex"
Expert. Expects efficiency, hates hand-holding.

**Behaviors**: Skips onboarding, looks for keyboard shortcuts, tries batch operations, frustrated by unnecessary steps.

**Red Flags**:
- Forced tutorials / unskippable onboarding
- No keyboard navigation for primary actions
- Slow unskippable animations
- One-at-a-time workflows where batch is natural
- Redundant confirmation for low-risk actions

---

## 2. Confused First-Timer — "Jordan"
Never used this type of product. Will abandon rather than figure it out.

**Behaviors**: Reads everything, hesitates before clicking, looks for help constantly, takes labels literally.

**Red Flags**:
- Icon-only navigation without labels
- Technical jargon without explanation
- No visible help option
- Ambiguous next steps after actions
- No success confirmation

---

## 3. Accessibility-Dependent User — "Sam"
Uses screen reader, keyboard-only. May have low vision or motor impairment.

**Behaviors**: Tabs through linearly, relies on ARIA, can't see hover states, needs 4.5:1 contrast, may zoom 200%.

**Red Flags**:
- Click-only interactions with no keyboard alternative
- Missing/invisible focus indicators
- Meaning conveyed by color alone
- Unlabeled form fields or buttons
- Custom components breaking screen reader flow

---

## 4. Deliberate Stress Tester — "Riley"
Tests edge cases, unexpected inputs, probes for gaps.

**Behaviors**: Tests 0 items/1000 items, submits emoji/RTL text, refreshes mid-flow, looks for inconsistencies.

**Red Flags**:
- Features that silently fail
- Error handling exposing technical details
- Empty states showing nothing useful
- Data lost on refresh/navigation
- Inconsistent behavior between similar interactions

---

## 5. Distracted Mobile User — "Casey"
One-handed, frequently interrupted, slow connection.

**Behaviors**: Thumb-only, switches apps mid-flow, low attention span, prefers taps over typing.

**Red Flags**:
- Important actions at top of screen (unreachable by thumb)
- No state persistence on tab switch
- Large text inputs where selection would work
- Heavy assets on every page
- Tiny tap targets or targets too close together

---

## Selection Guide

| Interface Type | Primary Personas |
|---|---|
| Landing page | Jordan, Riley, Casey |
| Dashboard/admin | Alex, Sam |
| E-commerce | Casey, Riley, Jordan |
| Onboarding | Jordan, Casey |
| Data/analytics | Alex, Sam |
| Form/wizard | Jordan, Sam, Casey |
| **Educational/children** | Jordan, Casey, + project-specific |

---

## Project-Specific Personas
If `.impeccable.md` contains Design Context, derive 1-2 additional personas from audience info:

```
### [Role] — "[Name]"
**Profile**: [2-3 characteristics from Design Context]
**Behaviors**: [3-4 specific behaviors]
**Red Flags**: [3-4 things that would alienate this user]
```

Only when real context exists. Don't invent.
