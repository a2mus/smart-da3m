# Production Deployment Guide

## Ihsane MVP Platform - Production Setup
**Domain:** `ihsan-dz.duckdns.org`  
**Server:** Caddy (Automatic HTTPS)  
**CI/CD:** GitHub Actions (Auto-deploy on push to main)

---

## 🚀 Quick Deploy Options

### Option 1: Automatic (Recommended)
Push to `main` branch → GitHub Actions deploys automatically

### Option 2: Manual
```bash
./deploy.sh
```

See [CI/CD Setup](CI_CD_SETUP.md) for GitHub Actions configuration.

---

## Quick Start (5 minutes)

### 1. Prepare Environment

```bash
cd /path/to/ihsane-platform

# Copy environment template
cp .env.prod.example .env

# Edit with your secure values
nano .env
```

**Required changes in `.env`:**
```bash
POSTGRES_PASSWORD=your_strong_password_here
SECRET_KEY=your_32_character_secret_key_here
```

### 2. Deploy

```bash
./deploy.sh
```

That's it! Your application will be available at:
- **Website:** https://ihsan-dz.duckdns.org
- **API Docs:** https://ihsan-dz.duckdns.org/docs

---

## Detailed Setup

### Prerequisites

Your VPS needs:
- Docker 20.10+
- Docker Compose 2.0+
- Ports 80 and 443 open
- At least 2GB RAM, 10GB disk

### Step-by-Step Installation

#### 1. Install Docker (if not installed)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

#### 2. Configure Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 443/udp   # HTTP/3
sudo ufw enable

# Verify
sudo ufw status
```

#### 3. Clone/Upload Project

```bash
git clone https://github.com/your-org/ihsane-platform.git
cd ihsane-platform
```

#### 4. Create Environment File

```bash
cp .env.prod.example .env
nano .env
```

**Generate strong passwords:**
```bash
# Generate a secure SECRET_KEY
openssl rand -hex 32

# Generate a secure DB password
openssl rand -base64 24
```

#### 5. Deploy

```bash
./deploy.sh
```

---

## Architecture: Caddy-Only

We use **Caddy** as the single entry point for all web traffic. Caddy handles:
- ✅ Automatic HTTPS (Let's Encrypt)
- ✅ Reverse proxy to backend API
- ✅ Static file serving for Vue.js frontend

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│              Caddy                  │
│  ┌───────────────────────────────┐  │
│  │  HTTPS (443) + HTTP/2 + HTTP/3 │  │
│  │  Let's Encrypt SSL (auto)      │  │
│  └───────────────────────────────┘  │
│                │                     │
│       ┌────────┴────────┐            │
│       ▼                 ▼            │
│  ┌──────────┐      ┌──────────┐     │
│  │  Static  │      │  Reverse │     │
│  │  Files   │      │  Proxy   │     │
│  │ (Vue.js) │      │ (API)    │     │
│  └──────────┘      └────┬─────┘     │
└─────────────────────────┼───────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
            ┌──────────┐  ┌──────────┐
            │ Backend  │  │  Static  │
            │(FastAPI) │  │  Volume  │
            └────┬─────┘  └──────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    ┌──────┐ ┌──────┐ ┌──────────┐
    │Postgre│ │Valkey│ │ Celery   │
    │SQL   │ │(Redis)│ │ Workers  │
    └──────┘ └──────┘ └──────────┘
```

### Why Caddy-Only?

**Decision:** We chose Caddy over Caddy+Nginx for simplicity.

**Rationale:**
- For an MVP with <500 users, Caddy's static file serving is more than adequate
- One less container to maintain
- Automatic HTTPS eliminates certificate management overhead
- Single configuration file (`Caddyfile`)
- Native HTTP/3 support

**Trade-off:** Nginx is ~10-20% faster at serving static files, but this difference is negligible at our scale. If we grow beyond ~5000 concurrent users, we can add Nginx or a CDN later without major changes.

See: `memory-bank/core/decisionLog.md` for full decision record.

---

## Management Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f caddy
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Stop Services

```bash
# Stop but keep data
docker-compose -f docker-compose.prod.yml down

# Stop and remove ALL data (⚠️ DANGEROUS)
docker-compose -f docker-compose.prod.yml down -v
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy (rebuilds frontend static files + restarts all services)
./deploy.sh
```

**Note on Frontend Updates:**
The frontend is built once at deploy time and served as static files by Caddy. When you update the frontend code:
1. Static files are rebuilt during `./deploy.sh`
2. Caddy automatically serves the new files (no restart needed for static file changes)
3. Users will get the new version on next page load (no caching for HTML files)

### Database Operations

```bash
# Access database shell
docker-compose -f docker-compose.prod.yml exec postgres psql -U ihsane_user -d ihsane

# Run migrations manually
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create migration
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "description"
```

### Backup Database

```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U ihsane_user ihsane > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
cat backup_file.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U ihsane_user -d ihsane
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check for port conflicts
sudo lsof -i :80
sudo lsof -i :443

# View detailed logs
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### HTTPS Not Working

```bash
# Check Caddy logs
docker-compose -f docker-compose.prod.yml logs caddy

# Verify domain points to this server
nslookup ihsan-dz.duckdns.org

# Check Caddy can reach Let's Encrypt
docker-compose -f docker-compose.prod.yml exec caddy wget -qO- https://acme-v02.api.letsencrypt.org/directory
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify credentials
docker-compose -f docker-compose.prod.yml exec postgres psql -U ihsane_user -d ihsane -c "\conninfo"
```

### 502 Bad Gateway

```bash
# Backend might be down
docker-compose -f docker-compose.prod.yml ps backend
docker-compose -f docker-compose.prod.yml logs backend

# Check if backend responds
docker-compose -f docker-compose.prod.yml exec caddy wget -qO- http://backend:8000/health
```

---

## Security Considerations

### Firewall Rules

Only these ports should be open:
- **22** - SSH (restrict to your IP if possible)
- **80** - HTTP (redirects to HTTPS)
- **443** - HTTPS
- **443/udp** - HTTP/3

### Environment Variables

Never commit `.env` file to git:
```bash
# Make sure .env is in .gitignore
git check-ignore -v .env
```

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
./deploy.sh
```

### SSL/TLS

Caddy automatically:
- Obtains certificates from Let's Encrypt
- Renews certificates before expiry
- Implements OCSP stapling
- Uses modern TLS versions (1.2+)

---

## Monitoring

### Check Service Health

```bash
# Backend health
curl https://ihsan-dz.duckdns.org/api/health

# Full status
docker-compose -f docker-compose.prod.yml ps
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused data
docker system prune -a
```

---

## DuckDNS Setup (if needed)

If you need to update your DuckDNS IP:

```bash
# Install DuckDNS client
cd ~
mkdir duckdns
cd duckdns

# Create update script
cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=ihsan-dz&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF
chmod 700 duck.sh

# Run every 5 minutes via cron
crontab -e
# Add: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

Get your token from: https://www.duckdns.org

---

## Support

For issues:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify `.env` configuration
3. Check firewall settings
4. Ensure domain points to correct IP
