# CI/CD Setup - GitHub Actions

This project uses **GitHub Actions** for continuous deployment. Every push to `main` or `master` branch automatically deploys to production.

---

## Workflow Overview

```
Push to main/master
       │
       ▼
┌──────────────┐
│  Run Tests   │  ← Backend (pytest) + Frontend (build)
└──────┬───────┘
       │ (only if tests pass)
       ▼
┌──────────────┐
│   Deploy     │  ← SSH to VPS, pull code, run deploy.sh
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Verify     │  ← Health check on https://ihsan-dz.duckdns.org
└──────────────┘
```

---

## Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### 1. VPS_HOST
Your VPS IP address or domain name.
```
Example: 203.0.113.1 or ihsan-dz.duckdns.org
```

### 2. VPS_USER
The SSH user on your VPS (should have Docker permissions).
```
Example: root or ubuntu or deploy
```

### 3. VPS_SSH_KEY
The **private** SSH key for authenticating to your VPS.

**How to generate:**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# Copy the PUBLIC key to your VPS
cat ~/.ssh/github_actions_deploy.pub
# Add this to /home/YOUR_USER/.ssh/authorized_keys on VPS

# The PRIVATE key goes to GitHub secrets
cat ~/.ssh/github_actions_deploy
```

### 4. DEPLOY_PATH
The absolute path to the project on your VPS.
```
Example: /home/ubuntu/ihsane-platform or /opt/ihsane
```

---

## Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

| Secret Name | Value |
|-------------|-------|
| `VPS_HOST` | Your VPS IP or domain |
| `VPS_USER` | SSH username |
| `VPS_SSH_KEY` | Private SSH key (entire content including BEGIN/END lines) |
| `DEPLOY_PATH` | `/path/to/project` |

---

## VPS Setup for CI/CD

### 1. Create Deploy User (Recommended)

```bash
# On your VPS
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo usermod -aG sudo deploy
```

### 2. Add SSH Key

```bash
# On VPS, as the deploy user
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh

# Add the public key from GitHub Actions
echo "ssh-ed25519 AAAA... github-actions-deploy" >> /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 3. Ensure .env Exists on VPS

The deployment script needs the `.env` file to be present:

```bash
# On VPS, in your project directory
cd /path/to/ihsane-platform
cp .env.prod.example .env
nano .env  # Edit with your production values
```

**Important:** Never commit `.env` to GitHub!

### 4. Test SSH Access

From your local machine:
```bash
ssh -i ~/.ssh/github_actions_deploy deploy@YOUR_VPS_IP
cd /path/to/ihsane-platform
./deploy.sh
```

If this works, the GitHub Actions workflow should work too.

---

## How It Works

### 1. Trigger
Push to `main` or `master` branch triggers the workflow.

You can also trigger manually:
- Go to **Actions** tab in GitHub
- Select **Deploy to Production**
- Click **Run workflow**

### 2. Testing Phase
```yaml
- Run backend tests (pytest)
- Build frontend (ensures no build errors)
```

If tests fail, deployment stops.

### 3. Deployment Phase
```yaml
- SSH to VPS
- git pull latest code
- Run ./deploy.sh
```

### 4. Verification Phase
```yaml
- Wait 30 seconds for services to start
- Check /api/health endpoint
- Retry up to 5 times
```

If verification fails, the workflow reports failure (but the deployment may still be running on VPS).

---

## Monitoring Deployments

### GitHub Actions Tab
- View all workflow runs
- See logs for each step
- Check success/failure status

### VPS Logs
```bash
# On VPS, view deployment logs
cd /path/to/ihsane-platform
docker-compose -f docker-compose.prod.yml logs -f

# Or view specific service
docker-compose -f docker-compose.prod.yml logs -f caddy
```

---

## Troubleshooting

### Deployment Fails at SSH Step

**Error:** `Permission denied (publickey)`

**Solution:**
```bash
# On VPS, check SSH key is correct
cat /home/YOUR_USER/.ssh/authorized_keys

# Ensure correct permissions
chmod 700 /home/YOUR_USER/.ssh
chmod 600 /home/YOUR_USER/.ssh/authorized_keys

# Test from local machine
ssh -i ~/.ssh/github_actions_deploy YOUR_USER@VPS_IP
```

### Deployment Fails at Docker Step

**Error:** `Cannot connect to Docker daemon`

**Solution:**
```bash
# On VPS, add user to docker group
sudo usermod -aG docker YOUR_USER
newgrp docker

# Or run Docker without sudo (log out and back in)
docker ps  # Should work without sudo
```

### Deployment Succeeds but App Not Working

Check logs:
```bash
# On VPS
cd /path/to/ihsane-platform
docker-compose -f docker-compose.prod.yml logs --tail=100

# Check if containers are running
docker-compose -f docker-compose.prod.yml ps
```

Common issues:
- `.env` file missing or has default values
- Port 80/443 in use by another service
- Database migrations failed

### Health Check Fails

If deployment succeeds but health check fails:
```bash
# Test manually
curl https://ihsan-dz.duckdns.org/api/health

# Check Caddy can reach backend
docker-compose -f docker-compose.prod.yml exec caddy wget -qO- http://backend:8000/health
```

---

## Security Considerations

### SSH Key Security
- Use a dedicated SSH key only for GitHub Actions
- Store private key only in GitHub Secrets
- Use Ed25519 keys (more secure than RSA)
- Rotate keys periodically

### Principle of Least Privilege
- Create a dedicated deploy user (not root)
- Only give Docker permissions
- No password login (key only)
- Restrict SSH to specific IPs if possible

### Secret Management
- Never commit `.env` files
- Never log secrets in workflow
- Use GitHub Secrets for all sensitive data

---

## Manual Deployment (Fallback)

If GitHub Actions is down or you need to deploy manually:

```bash
# SSH to VPS
ssh YOUR_USER@YOUR_VPS_IP

# Go to project
cd /path/to/ihsane-platform

# Pull latest
git pull origin main

# Deploy
./deploy.sh
```

---

## Workflow File Location

`.github/workflows/deploy.yml`

You can modify this file to:
- Add more tests
- Change deployment strategy
- Add notifications (Slack, Discord, email)
- Add staging environment

---

*Last updated: 2026-04-11*
