# Decision Log

**Project:** Ihsane MVP Platform (منصة إحسان)  
**Domain:** ihsan-dz.duckdns.org

---

## DEC-001: Reverse Proxy and Static File Serving Architecture

**Date:** 2026-04-11  
**Status:** ✅ Accepted  
**Context:** Need to choose web server architecture for production deployment

### Decision
Use **Caddy-only architecture** - Caddy handles:
1. Automatic HTTPS (Let's Encrypt)
2. Reverse proxy to backend API
3. Static file serving for Vue.js frontend

### Alternatives Considered

#### Option A: Caddy + Nginx (Rejected)
- **Description:** Caddy for HTTPS/routing, Nginx inside frontend container for static files
- **Pros:** 
  - Nginx is extremely optimized for static file serving
  - Industry-standard pattern
  - Separation of concerns
- **Cons:**
  - Extra container complexity
  - More moving parts to maintain
  - Minimal performance gain for MVP scale (<500 users)

#### Option B: Nginx + Certbot (Rejected)
- **Description:** Nginx for everything with Certbot for SSL
- **Pros:**
  - Very mature, well-documented
  - Battle-tested in production
- **Cons:**
  - Manual SSL certificate management
  - More complex configuration
  - No HTTP/3 support out of the box

#### Option C: Caddy-only (✅ Selected)
- **Description:** Caddy handles HTTPS, routing, and static file serving
- **Pros:**
  - **Simplicity:** Single tool for all web serving needs
  - **Automatic HTTPS:** Zero-config SSL certificates via Let's Encrypt
  - **Modern:** Native HTTP/2 and HTTP/3 support
  - **Performance:** Adequate for MVP scale (Caddy's static file serving is efficient)
  - **Maintainability:** Single configuration file (Caddyfile)
  - **Resource efficiency:** Fewer containers running
- **Cons:**
  - Nginx is ~10-20% faster at static file serving (negligible for MVP)
  - Less granular control than Nginx for advanced use cases

### Rationale

For the Ihsane MVP with <500 concurrent users:

1. **Simplicity over micro-optimization:** The performance difference between Caddy and Nginx for static files is negligible at this scale. Developer/maintainer time is more valuable than the marginal performance gain.

2. **Operational ease:** Caddy's automatic HTTPS eliminates certificate management overhead. This is crucial for a small team running a pilot program.

3. **Modern protocol support:** HTTP/3 support out of the box improves user experience, especially on mobile networks in Algeria.

4. **Single responsibility:** Caddy handles the edge (HTTPS + routing) while the backend containers handle application logic. The frontend is built as static files and served directly by Caddy.

5. **Future flexibility:** If we need to scale to thousands of users and require Nginx's advanced features, we can add it later without major architectural changes.

### Implementation

**Services:**
- `caddy`: Handles HTTPS, reverse proxy to backend, serves static files
- `backend`: FastAPI application (exposed only internally)
- `frontend-build`: One-time build container that outputs static files to shared volume
- `postgres`: PostgreSQL database
- `valkey`: Redis-compatible cache
- `celery-worker`/`celery-beat`: Background task processing

**Flow:**
```
Internet → Caddy (443) → Static Files (Vue.js)
                    ↓
               Backend API (8000)
                    ↓
            Database/Cache/Workers
```

### Consequences

**Positive:**
- Simpler deployment with fewer containers
- Zero-config SSL certificates
- Single configuration file to maintain
- Reduced resource usage
- Faster deployment times

**Negative:**
- If we scale beyond ~5000 users, may need to add Nginx or CDN for static files
- Less community knowledge about Caddy compared to Nginx (but well-documented)

### Related Files
- `Caddyfile` - Main Caddy configuration
- `docker-compose.prod.yml` - Production orchestration
- `deploy.sh` - Deployment script
- `DEPLOY.md` - Deployment documentation

### References
- Caddy docs: https://caddyserver.com/docs/
- Let's Encrypt: https://letsencrypt.org/
- HTTP/3: https://en.wikipedia.org/wiki/HTTP/3

---

## DEC-002: SSL/TLS Certificate Management

**Date:** 2026-04-11  
**Status:** ✅ Accepted  
**Context:** How to manage SSL certificates for HTTPS

### Decision
Use Caddy's **Automatic HTTPS** with Let's Encrypt

### Rationale
- Zero configuration required
- Automatic renewal (no cron jobs needed)
- Free (Let's Encrypt)
- Industry standard

### Implementation
- Domain: `ihsan-dz.duckdns.org`
- Email: `admin@ihsan-dz.duckdns.org` (for Let's Encrypt notifications)
- HTTP challenge (port 80) automatically handled by Caddy

### Related Decisions
- DEC-001 (Caddy-only architecture enables this)

---

## DEC-003: Frontend Static File Build Strategy

**Date:** 2026-04-11  
**Status:** ✅ Accepted  
**Context:** How to build and serve Vue.js frontend in production

### Decision
Use **build-time container** that outputs static files to shared Docker volume

### Implementation
1. `frontend-build` service runs Node container
2. Builds Vue.js app with `VITE_API_URL` pointing to production API
3. Outputs to `frontend_dist` volume
4. Caddy mounts this volume read-only and serves files directly

### Rationale
- No Node.js runtime needed in production (smaller attack surface)
- Static files served directly by Caddy (efficient)
- Environment variables baked in at build time (secure)
- Simple rollback (just rebuild and restart Caddy)

### Alternative: Runtime SSR (Rejected)
- Would require Node.js container running constantly
- More complex, more resource usage
- Not needed for SPA architecture

---

## DEC-004: Domain and DNS Strategy

**Date:** 2026-04-11  
**Status:** ✅ Accepted  
**Context:** Domain for production deployment

### Decision
Use **DuckDNS subdomain**: `ihsan-dz.duckdns.org`

### Rationale
- Free dynamic DNS service
- Easy to update if VPS IP changes
- No domain purchase required for pilot
- Can migrate to custom domain later without code changes

### Future
- Pilot: `ihsan-dz.duckdns.org`
- Production: Custom domain (e.g., `ihsane.education`)

### Related Files
- `Caddyfile` - Domain configuration
- `docker-compose.prod.yml` - Domain environment variable

---

## Template for Future Decisions

```markdown
## DEC-XXX: [Title]

**Date:** YYYY-MM-DD  
**Status:** [Proposed | Accepted | Deprecated | Superseded by DEC-XXX]  
**Context:** [What is the issue we're deciding?]

### Decision
[What did we decide?]

### Alternatives Considered
[What else did we consider?]

### Rationale
[Why did we choose this option?]

### Consequences
**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Drawback 1]
- [Drawback 2]

### Related Files
- [File links]

### Related Decisions
- [Links to other decisions]
```

---

## DEC-005: CI/CD Pipeline Architecture

**Date:** 2026-04-11  
**Status:** ✅ Accepted  
**Context:** Need automated deployment when code is pushed to main branch

### Decision
Use **GitHub Actions** with **SSH-based deployment** to VPS

### Alternatives Considered

#### Option A: GitHub Actions + Docker Registry (Rejected)
- **Description:** Build Docker images in GitHub Actions, push to registry, pull on VPS
- **Pros:**
  - Clean separation of build and deploy
  - Can rollback to specific image versions
  - No build dependencies on VPS
- **Cons:**
  - Requires Docker Hub or GitHub Container Registry account
  - More complex setup
  - Storage costs for images
  - Slower (build + push + pull vs just pull + build)

#### Option B: Self-hosted GitHub Runner on VPS (Rejected)
- **Description:** Run GitHub Actions runner directly on the VPS
- **Pros:**
  - No SSH key management
  - Direct access to Docker daemon
  - Faster (no SSH overhead)
- **Cons:**
  - Requires maintaining runner software
  - Security concerns (GitHub has access to production server)
  - Runner needs to always be online
  - More resource usage on VPS

#### Option C: GitHub Actions + SSH Deploy (✅ Selected)
- **Description:** GitHub Actions SSH to VPS, pull code, run deploy script
- **Pros:**
  - **Simple:** Uses existing GitHub infrastructure
  - **Fast:** Just git pull + docker build (cached layers)
  - **Secure:** SSH key authentication, no registry needed
  - **Transparent:** All steps visible in GitHub Actions logs
  - **Flexible:** Easy to customize deployment steps
- **Cons:**
  - Requires SSH key management
  - VPS must be accessible from GitHub's IP ranges
  - Build happens on VPS (requires Docker on VPS)

### Rationale

For a small team running an MVP pilot:

1. **Simplicity:** SSH-based deployment is straightforward and uses tools we already have (Docker, git, SSH).

2. **Cost:** No need for Docker Hub or other registry (free tier limits could be hit).

3. **Speed:** With Docker layer caching on VPS, subsequent deployments are fast.

4. **Security:** SSH keys are well-understood and can be rotated easily. No need to give GitHub direct infrastructure access via self-hosted runners.

5. **Transparency:** The workflow file clearly shows what happens during deployment.

### Implementation

**Workflow:**
```yaml
Push to main
  │
  ▼
Run Tests (backend + frontend build)
  │ (only if tests pass)
  ▼
SSH to VPS
  │
  ▼
git pull origin main
  │
  ▼
./deploy.sh
  │
  ▼
Verify health endpoint
```

**Required Secrets:**
- `VPS_HOST`: VPS IP or domain
- `VPS_USER`: SSH username
- `VPS_SSH_KEY`: Private SSH key
- `DEPLOY_PATH`: Absolute path to project on VPS

**Security Measures:**
- Dedicated deploy user (not root)
- SSH key only (no password)
- Docker group membership for deploy user
- `.env` file never committed to git

### Consequences

**Positive:**
- Automatic deployment on every push to main
- Tests run before deployment (prevents broken deploys)
- Health check verification after deployment
- Manual workflow dispatch available for emergency deploys
- All deployment history visible in GitHub Actions tab

**Negative:**
- VPS must be online and accessible
- Build happens on VPS (uses VPS resources)
- If GitHub Actions is down, manual deployment required
- SSH key rotation needed periodically

### Related Files
- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `CI_CD_SETUP.md` - Setup and troubleshooting guide
- `deploy.sh` - Deployment script

### References
- GitHub Actions: https://docs.github.com/en/actions
- SSH Key Management: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- webfactory/ssh-agent: https://github.com/webfactory/ssh-agent

---

*Last updated: 2026-04-11*
