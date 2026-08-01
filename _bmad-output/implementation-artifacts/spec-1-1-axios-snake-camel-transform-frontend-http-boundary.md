---
title: 'Story 1.1: Axios Snake↔Camel Transform & Frontend HTTP Boundary'
type: 'refactor'
created: '2026-08-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** Backend API payloads use snake_case (`access_token`, `refresh_token`, `parent_id`, etc.), but Vue frontend components and stores require camelCase (`accessToken`, `refreshToken`, `parentId`), creating manual key transformation boilerplate across stores and services.

**Approach:** Implement recursive snake_case ↔ camelCase interceptors in `frontend/src/services/api.ts` to transform all incoming API response bodies to camelCase and outgoing API request payloads to snake_case automatically, and refactor Pinia stores (such as `authStore`) to consume camelCase properties directly.

## Boundaries & Constraints

**Always:**
- Transform all incoming JSON response data recursively from `snake_case` keys to `camelCase` keys in Axios response interceptor.
- Transform all outgoing JSON request data recursively from `camelCase` keys to `snake_case` keys in Axios request interceptor (excluding `FormData` or non-JSON payloads).
- Maintain TypeScript typing compatibility across `authStore` and API service helpers.

**Block If:**
- API response transformation breaks file upload / `FormData` payload structures.

**Never:**
- Allow Vue components or Pinia stores to manually read or map raw `snake_case` properties.
- Mutate original request/response headers or break JWT `Authorization` header placement.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Response Transform | `{"access_token": "abc", "refresh_token": "xyz"}` | `{"accessToken": "abc", "refreshToken": "xyz"}` | Return clean camelCase object |
| Request Transform | `{ parentEmail: "a@b.com", pinCode: "1234" }` | `{ parent_email: "a@b.com", pin_code: "1234" }` | Transformed before HTTP send |
| Nested Object Transform | `{ user: { parent_id: "123" } }` | `{ user: { parentId: "123" } }` | Recursive conversion applied |
| Array of Objects | `[{ user_id: "1" }, { user_id: "2" }]` | `[{ userId: "1" }, { userId: "2" }]` | Array elements converted recursively |

</intent-contract>

## Code Map

- `frontend/src/services/api.ts` -- Axios instance configuration, request & response key-casing interceptors, and API helper functions.
- `frontend/src/stores/auth.ts` -- Pinia auth store handling authentication state and consuming camelCase API responses.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/services/api.ts` -- Add camelCase/snake_case recursive conversion interceptors to Axios instance and update `authApi` payload keys -- Ensures automatic HTTP boundary key casing.
- [x] `frontend/src/stores/auth.ts` -- Refactor `loginWithEmail`, `loginWithPin`, and `refreshAccessToken` to destructure `accessToken`/`refreshToken` -- Removes manual snake_case destructuring.

**Acceptance Criteria:**
- Given Axios interceptors are configured in `src/services/api.ts`, when a response with `access_token` and `refresh_token` arrives, then it is transformed to `accessToken` and `refreshToken` before reaching services and stores.
- Given request payloads are sent via Axios, when payload contains `camelCase` keys, then keys are converted to `snake_case` before network dispatch.
- Given `auth.ts` store actions run, when handling login/refresh, then `accessToken` and `refreshToken` are read directly from `response.data` without manual key renaming.

## Spec Change Log

## Review Triage Log

### 2026-08-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Design Notes

Recursive conversion utility functions (`keysToCamelCase` and `keysToSnakeCase`) handle nested objects and arrays safely, bypassing instances of `FormData`, `File`, `Blob`, `Date`, and `RegExp`.

## Verification

**Commands:**
- `pnpm --filter frontend test` -- expected: All frontend unit tests pass
- `pnpm --filter frontend type-check` -- expected: No TypeScript compilation errors

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented automatic HTTP boundary key transformations between `snake_case` (backend) and `camelCase` (frontend) via Axios request and response interceptors, and refactored the `authStore` Pinia store to read `accessToken` and `refreshToken` directly.
- **Files Modified**:
  - `frontend/src/services/api.ts`: Added `keysToCamelCase` response interceptor and `keysToSnakeCase` request interceptor; updated `authApi` helper payloads.
  - `frontend/src/stores/auth.ts`: Refactored `loginWithEmail`, `loginWithPin`, and `refreshAccessToken` to destructure `accessToken` and `refreshToken`.
