---
title: 'Story 11.3: Defensive API Payload Normalization in dashboardService'
type: 'bugfix'
created: '2026-08-04'
status: 'review'
baseline_revision: '87d4f7ce4b8e69574d797fc58ae7adbc15632cdf'
final_revision: '87d4f7ce4b8e69574d797fc58ae7adbc15632cdf'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/planning-artifacts/epics.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `dashboardService.getChildrenList()` directly invoked `response.data.map(...)` assuming `response.data` is always a raw array (`[...]`). If an endpoint wrapper returns an envelope payload (`{ items: [...] }` or `{ children: [...] }`), `response.data.map` threw a `TypeError: response.data.map is not a function`.

**Approach:** Defensively extract the raw array from `response.data` using `Array.isArray(response.data) ? response.data : (response.data?.items || response.data?.children || [])` before mapping.

## Boundaries & Constraints

**Always:** Ensure `getChildrenList()` cleanly parses both raw arrays (`[...]`) and envelope object payloads (`{ items: [...] }` / `{ children: [...] }`).

</intent-contract>

## Code Map

- `frontend/src/services/dashboardService.ts` -- Dashboard service containing `getChildrenList()`

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/services/dashboardService.ts` -- Normalize `response.data` defensively in `getChildrenList()`

**Acceptance Criteria:**
- Given `getChildrenList()` receives either a raw array `[...]` or an envelope object `{ items: [...] }` / `{ children: [...] }`
- When called
- Then it returns a normalized array of `ChildSummary` objects without throwing TypeError exceptions
