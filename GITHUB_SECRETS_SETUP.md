# GitHub Secrets Setup Guide

**Purpose:** Configure GitHub Actions to auto-deploy to your VPS  
**Time:** ~10 minutes  
**Difficulty:** Easy

---

## Overview

We need to add 4 secrets to GitHub:

1. `VPS_HOST` - Your server address
2. `VPS_USER` - SSH username
3. `VPS_SSH_KEY` - Private SSH key
4. `DEPLOY_PATH` - Where code lives on VPS

---

## Step 1: Get Your VPS Information

### Find Your VPS Host

```bash
# On your VPS, run:
curl ifconfig.me
# or
curl icanhazip.com
```

**Write down:** Your VPS IP address (e.g., `203.0.113.1`)

---

## Step 2: Choose/Create Deploy User

### Option A: Use Existing User (Quick)

If you already have a user on VPS with Docker access, use that.

```bash
# Check if user has Docker access
ssh your-existing-user@your-vps-ip docker ps
```

If this works, use `your-existing-user` as `VPS_USER`.

### Option B: Create Dedicated Deploy User (Recommended)

```bash
# SSH to your VPS as root or sudo user
ssh root@your-vps-ip

# Create deploy user
sudo useradd -m -s /bin/bash deploy

# Add to docker group (so deploy user can run Docker)
sudo usermod -aG docker deploy

# Optional: Add to sudoers (for some admin tasks)
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose" | sudo tee /etc/sudoers.d/deploy
```

**Write down:** Username (e.g., `deploy` or `ubuntu` or `root`)

---

## Step 3: Generate SSH Key

On your **local machine** (not VPS):

```bash
# Generate new SSH key for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/ihsane_github_deploy

# When prompted for passphrase, press Enter (no passphrase)
# This creates two files:
#   ~/.ssh/ihsane_github_deploy      (PRIVATE key - goes to GitHub)
#   ~/.ssh/ihsane_github_deploy.pub  (PUBLIC key - goes to VPS)
```

**Write down:** Keep terminal open, we'll use these files

---

## Step 4: Add Public Key to VPS

### Method 1: SSH Copy (Easiest)

```bash
# From your local machine
cat ~/.ssh/ihsane_github_deploy.pub

# Copy the output (starts with ssh-ed25519...)
```

Then on your **VPS**:

```bash
# Switch to deploy user
sudo su - deploy

# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add the public key
nano ~/.ssh/authorized_keys
# Paste the key you copied, save (Ctrl+O, Enter, Ctrl+X)

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys

# Test from your LOCAL machine:
exit  # Exit deploy user if you were in it
```

Back on **local machine**:

```bash
# Test SSH connection (should NOT ask for password)
ssh -i ~/.ssh/ihsane_github_deploy deploy@your-vps-ip

# If it works, you'll be logged into VPS
# Type 'exit' to logout
```

### Method 2: Using ssh-copy-id

```bash
# From local machine
ssh-copy-id -i ~/.ssh/ihsane_github_deploy.pub deploy@your-vps-ip

# Test
ssh -i ~/.ssh/ihsane_github_deploy deploy@your-vps-ip
```

---

## Step 5: Prepare Deploy Path on VPS

```bash
# SSH to VPS (as deploy user or with sudo)
ssh deploy@your-vps-ip

# Create project directory
sudo mkdir -p /opt/ihsane-platform
sudo chown deploy:deploy /opt/ihsane-platform

# Clone your repository
cd /opt/ihsane-platform
git clone https://github.com/YOUR_USERNAME/ihsane-platform.git .

# Or if using SSH:
# git clone git@github.com:YOUR_USERNAME/ihsane-platform.git .

# Verify it's there
ls -la
```

**Write down:** Path (e.g., `/opt/ihsane-platform` or `/home/deploy/ihsane-platform`)

---

## Step 6: Add Secrets to GitHub

### 6.1 Go to GitHub Secrets Page

1. Open your repository on GitHub
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 6.2 Add Each Secret

#### Secret 1: VPS_HOST

```
Name: VPS_HOST
Value: YOUR_VPS_IP_OR_DOMAIN
```

Examples:
- `203.0.113.1`
- `ihsan-dz.duckdns.org`

#### Secret 2: VPS_USER

```
Name: VPS_USER
Value: deploy
```

(Or whatever username you chose: `ubuntu`, `root`, etc.)

#### Secret 3: VPS_SSH_KEY ⚠️ IMPORTANT

```
Name: VPS_SSH_KEY
Value: [ENTIRE PRIVATE KEY CONTENT]
```

**To get the value:**

```bash
# On your local machine
cat ~/.ssh/ihsane_github_deploy
```

**Copy EVERYTHING including:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACB... (more lines)
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **Paste the ENTIRE content including the BEGIN/END lines**

#### Secret 4: DEPLOY_PATH

```
Name: DEPLOY_PATH
Value: /opt/ihsane-platform
```

(Or wherever you cloned the repo on VPS)

---

## Step 7: Verify Setup

### 7.1 Check Secrets Are Added

Go to GitHub → Settings → Secrets → Actions  
You should see 4 secrets:
- ✅ `VPS_HOST`
- ✅ `VPS_USER`
- ✅ `VPS_SSH_KEY`
- ✅ `DEPLOY_PATH`

### 7.2 Test Deployment

Make a small change and push:

```bash
# On your local machine
cd /path/to/ihsane-platform

# Make a small change
echo "# Auto-deploy test" >> README.md

# Commit and push
git add .
git commit -m "Test auto-deploy"
git push origin main
```

### 7.3 Watch the Magic

1. Go to GitHub → **Actions** tab
2. You should see a workflow running
3. Click on it to see live logs
4. Wait 2-3 minutes
5. Check https://ihsan-dz.duckdns.org

---

## Troubleshooting

### Error: "Permission denied (publickey)"

**Cause:** SSH key not set up correctly

**Fix:**
```bash
# On VPS, check authorized_keys
cat /home/deploy/.ssh/authorized_keys
# Should contain your public key

# Check permissions
ls -la /home/deploy/.ssh/
# Should be: drwx------ (700) for .ssh
# Should be: -rw------- (600) for authorized_keys

# Fix permissions if wrong
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### Error: "Cannot connect to Docker daemon"

**Cause:** Deploy user not in docker group

**Fix:**
```bash
# On VPS as root
sudo usermod -aG docker deploy

# Restart SSH session or run:
newgrp docker

# Verify
docker ps
```

### Error: "env file not found"

**Cause:** `.env` file missing on VPS

**Fix:**
```bash
# On VPS
cd /opt/ihsane-platform  # or your DEPLOY_PATH
cp .env.prod.example .env
nano .env
# Edit: POSTGRES_PASSWORD and SECRET_KEY
```

### Workflow Shows "Failed"

1. Go to GitHub → Actions
2. Click on the failed workflow
3. Look for red X marks
4. Read the error message
5. Common issues:
   - Wrong VPS_HOST
   - Wrong DEPLOY_PATH
   - Missing .env on VPS
   - Port 80/443 already in use

---

## Security Checklist

✅ SSH key is Ed25519 (modern, secure)  
✅ Private key has NO passphrase (needed for automation)  
✅ Private key stored ONLY in GitHub Secrets  
✅ Public key added ONLY to deploy user's authorized_keys  
✅ Deploy user has minimal permissions (docker group only)  
✅ `.env` file never committed to git  
✅ Secrets are encrypted by GitHub  

---

## Quick Reference

| Task | Command |
|------|---------|
| View secrets | GitHub → Settings → Secrets → Actions |
| Test SSH manually | `ssh -i ~/.ssh/ihsane_github_deploy deploy@VPS_IP` |
| View workflow logs | GitHub → Actions → Click workflow run |
| Re-run failed deploy | GitHub → Actions → Click workflow → Re-run jobs |
| Manual deploy | SSH to VPS and run `./deploy.sh` |

---

## Next Steps

1. ✅ Add the 4 secrets to GitHub
2. ✅ Make a test push
3. ✅ Watch deployment in Actions tab
4. ✅ Verify site is live
5. 🎉 Enjoy automatic deployments!

---

**Need help?** Check `CI_CD_SETUP.md` for more detailed troubleshooting.
