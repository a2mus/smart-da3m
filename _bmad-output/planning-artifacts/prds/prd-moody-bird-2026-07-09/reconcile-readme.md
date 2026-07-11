# Reconciliation: README.md (Arabic) → PRD + Addendum

**Source:** `README.md` (Arabic overview of the Ihsane Platform).
**Compared against:** `prd.md` + `addendum.md` (PRD artifact set, dated 2026-07-09).
**Goal:** Find product-level GAPS — content/detail present in the README but dropped, lost, or contradicted in the PRD.
**Scope rule:** Tooling trivia (pnpm vs npm, exact Python/Postgres version pins, local-dev commands) is intentionally NOT flagged, per the brief. Only product-level gaps: security detail, deployment/hosting specifics, feature nuance, project facts.

---

## Method

Read the README in full (198 lines, Arabic + English tech-stack blocks). Mapped each README section to its PRD/addendum counterpart. Flagged only items where the README carries a detail the PRD set fails to preserve or silently contradicts.

**Coverage summary:** Every README *feature* (adaptive diagnostic, remediation pathways, parent dashboard, expert analytics, pedagogical alerts, bilingual AR/FR) is fully captured and *expanded* by the PRD's FRs. The README's vision/mission/tone ("first digital companion," "rehumanizes learning") is preserved in PRD §1. The gaps are concentrated in **infrastructure/hosting**, one **security-detail** nuance, and a **project-fact** omission. No feature was dropped.

---

## Gaps Found

### GAP-1 — Cloudflare CDN dropped from the hosting story *(deployment/hosting; notable)*

- **README (l.79):** lists **"Cloudflare CDN"** as a core infrastructure component, alongside OVH Cloud hosting and Nginx.
- **PRD §10 (Performance NFRs):** states performance targets (FCP < 3s on 3G, P95 < 200ms, bundle < 200KB) but names **no CDN**.
- **PRD §11 (Cost/Platform constraints):** mentions only "OVH VPS + DuckDNS."
- **Addendum A2 (ADRs):** lists DEC-001 (Caddy-only edge), DEC-002 (Caddy auto-HTTPS), DEC-004 (DuckDNS subdomain). **No Cloudflare entry.**
- **Impact:** Either Cloudflare is still in the stack (then the PRD set under-documents a component that directly serves the §10 performance targets), or it was replaced by Caddy-at-the-edge (then that swap is an **unrecorded decision** — there is no ADR retiring Cloudflare). Either way, a reader reconciling the two sources cannot tell whether a CDN fronts the pilot deployment. Recommend PM confirm and either add a "DEC-006: Cloudflare retired in favor of Caddy" entry or document the CDN's role in §10.

### GAP-2 — Nginx → Caddy: silent contradiction *(deployment/hosting; notable)*

- **README (l.77):** lists **"Nginx" reverse proxy** as infrastructure.
- **Addendum A2, DEC-001:** ratifies **"Caddy-only edge (HTTPS + reverse proxy + static serving)"** — i.e., Nginx was replaced by Caddy.
- **PRD:** silent on the reverse-proxy choice.
- **Impact:** The addendum correctly records the *current* reality (Caddy), but **nowhere reconciles the contradiction** with the README's Nginx claim. A reader cross-checking sources sees two different reverse proxies with no explanation. Low product risk, but worth a one-line note in A2 ("README references Nginx; superseded by DEC-001 Caddy") so the audit trail is clean.

### GAP-3 — bcrypt hashing scope: student PINs not specified *(security detail; minor)*

- **README (l.155):** "bcrypt Hashing — لتشفير **كلمات المرور والرموز السرية**" — i.e., bcrypt is applied to **passwords AND secret codes/PINs**.
- **PRD FR-2:** specifies bcrypt-hashed storage for **parent/expert passwords** only.
- **PRD FR-1 (Student PIN login):** describes PIN auth but does **not** state that the PIN is bcrypt-hashed (or otherwise secured) at rest.
- **Impact:** A real security-relevant detail (how the child-facing credential is stored) is present in the README but not carried into the FR that governs student login. Recommend FR-1's "Consequences" add: "PIN codes are stored bcrypt-hashed, consistent with FR-2." Minor but closes a security-spec hole.

### GAP-4 — MIT License / open-source posture not recorded *(project fact; minor)*

- **README (l.182):** declares the project licensed under **MIT License** (links a `LICENSE` file), and (l.188) references a `CONTRIBUTING.md` for public contribution.
- **PRD + Addendum:** make **no mention** of license, open-source posture, or contribution model. §11 constraints cover privacy/cost/compliance/platform but not licensing.
- **Impact:** The README positions Ihsane as an openly-licensed, contribution-welcoming project; the PRD is neutral/silent. If the pilot product is indeed MIT-licensed and accepting contributions, that's a project-level fact worth a single line in §11 (Constraints) or the addendum. Not blocking, but currently lost.

---

## Considered and NOT flagged (intentional)

- **pnpm** (README l.119) vs the Vue 3 reality — tooling trivia, per brief.
- **PostgreSQL 16+ / Python 3.12+ / Node 20+** version pins — tooling trivia.
- **SQLAlchemy / Pydantic v2 / Alembic** — implementation libraries, not product-level.
- **Docker / docker-compose** quickstart — tooling.
- **JWT 30-min expiry** — PRD §4.1 & §10 cover it (and *expand* it with the 7-day refresh token the README omits).
- **CORS / RBAC / Rate limiting on auth / CSP headers** — all present in PRD §10; README adds no additional specificity here.
- **Project folder structure** (README §هيكل المشروع) — implementation layout, not product.
- **Integration-test command** (`pytest tests/integration/`) — testing mechanics.

---

## Verdict

**4 gaps, none blocking, two worth a PM action.** The PRD is materially faithful to the README at the product/feature level — nothing pedagogical or user-facing was lost. The drift is purely on the **infra/hosting** perimeter (Cloudflare CDN absent, Nginx↔Caddy contradiction unexplained), plus two minor spec-hygiene items (PIN hashing scope, license). Recommend:

1. **GAP-1 (Cloudflare):** confirm CDN status; add an ADR or a §10 note.
2. **GAP-2 (Nginx→Caddy):** one-line supersession note in addendum A2.
3. **GAP-3 (PIN bcrypt):** add a consequence line to FR-1.
4. **GAP-4 (MIT license):** optional one-liner in §11 or addendum.
