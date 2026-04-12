# GitHub Secrets Setup Checklist

**Task:** Configure GitHub Actions to auto-deploy to your VPS  
**Estimated Time:** 10-15 minutes  
**Status:** ⬜ Not Started

---

## Pre-Requirements

- [ ] You have a VPS running (Ubuntu/Debian recommended)
- [ ] Docker is installed on VPS (or you'll install it)
- [ ] You have SSH access to VPS
- [ ] Your code is on GitHub

---

## Step 1: Get VPS Information

- [ ] SSH to your VPS: `ssh root@YOUR_VPS_IP`
- [ ] Get your IP: `curl ifconfig.me`
- [ ] **Write down:** `VPS_HOST = ________________` (e.g., `203.0.113.1`)

---

## Step 2: Create Deploy User (Optional but Recommended)

On your VPS:

- [ ] Create user: `sudo useradd -m -s /bin/bash deploy`
- [ ] Add to docker group: `sudo usermod -aG docker deploy`
- [ ] **Write down:** `VPS_USER = deploy` (or use existing user)

---

## Step 3: Generate SSH Key (On Your Local Machine)

Open terminal on your local machine (NOT VPS):

- [ ] Run: `ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/ihsane_github_deploy`
- [ ] Press Enter when asked for passphrase (no passphrase needed)
- [ ] Two files created:
  - `~/.ssh/ihsane_github_deploy` (PRIVATE)
  - `~/.ssh/ihsane_github_deploy.pub` (PUBLIC)

---

## Step 4: Add Public Key to VPS

On your VPS (as the deploy user):

- [ ] Create SSH directory: `mkdir -p ~/.ssh`
- [ ] Set permissions: `chmod 700 ~/.ssh`
- [ ] Add public key:
  ```bash
  nano ~/.ssh/authorized_keys
  # Paste content of ~/.ssh/ihsane_github_deploy.pub from your local machine
  # Save: Ctrl+O, Enter, Ctrl+X
  ```
- [ ] Set permissions: `chmod 600 ~/.ssh/authorized_keys`

**Test the connection (on your local machine):**
- [ ] Run: `ssh -i ~/.ssh/ihsane_github_deploy deploy@YOUR_VPS_IP`
- [ ] Should log in without password
- [ ] Type `exit` to logout

---

## Step 5: Prepare Project on VPS

On your VPS:

- [ ] Create directory: `sudo mkdir -p /opt/ihsane-platform`
- [ ] Change ownership: `sudo chown deploy:deploy /opt/ihsane-platform`
- [ ] Clone repository:
  ```bash
  cd /opt/ihsane-platform
  git clone https://github.com/YOUR_USERNAME/ihsane-platform.git .
  ```
- [ ] Verify: `ls -la` (should show project files)
- [ ] **Write down:** `DEPLOY_PATH = /opt/ihsane-platform`

---

## Step 6: Get Private Key Content

On your local machine:

- [ ] Run: `cat ~/.ssh/ihsane_github_deploy`
- [ ] Copy the ENTIRE output including:
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  ... (many lines)
  -----END OPENSSH PRIVATE KEY-----
  ```
- [ ] Save this in a temporary text file (you'll paste it in GitHub)

---

## Step 7: Add Secrets to GitHub

Go to GitHub in your browser:

- [ ] Open your repository
- [ ] Click **Settings** tab
- [ ] In left sidebar, click **Secrets and variables** → **Actions**
- [ ] Click **New repository secret**

### Add Secret 1: VPS_HOST
- [ ] Name: `VPS_HOST`
- [ ] Value: `YOUR_VPS_IP` (from Step 1)
- [ ] Click **Add secret**

### Add Secret 2: VPS_USER
- [ ] Name: `VPS_USER`
- [ ] Value: `deploy` (or your username from Step 2)
- [ ] Click **Add secret**

### Add Secret 3: VPS_SSH_KEY ⚠️
- [ ] Name: `VPS_SSH_KEY`
- [ ] Value: Paste the ENTIRE private key from Step 6
- [ ] Click **Add secret**

### Add Secret 4: DEPLOY_PATH
- [ ] Name: `DEPLOY_PATH`
- [ ] Value: `/opt/ihsane-platform` (from Step 5)
- [ ] Click **Add secret**

### Verify All Secrets Added
- [ ] Go to Settings → Secrets → Actions
- [ ] Should see 4 secrets:
  - ✅ VPS_HOST
  - ✅ VPS_USER
  - ✅ VPS_SSH_KEY
  - ✅ DEPLOY_PATH

---

## Step 8: Prepare Environment File on VPS

On your VPS:

- [ ] Go to project: `cd /opt/ihsane-platform`
- [ ] Copy example: `cp .env.prod.example .env`
- [ ] Edit: `nano .env`
- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Change `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- [ ] Save: Ctrl+O, Enter, Ctrl+X

---

## Step 9: Test Automatic Deployment

On your local machine:

- [ ] Make a small change:
  ```bash
  cd /path/to/ihsane-platform
  echo "# Auto-deploy test" >> README.md
  ```
- [ ] Commit: `git add . && git commit -m "Test auto-deploy"`
- [ ] Push: `git push origin main`

Watch the deployment:
- [ ] Go to GitHub → **Actions** tab
- [ ] You should see a workflow running
- [ ] Click on it to see live logs
- [ ] Wait for green checkmark ✅

Verify it's live:
- [ ] Open: https://ihsan-dz.duckdns.org
- [ ] Should show your application

---

## Troubleshooting

If deployment fails, check:

- [ ] VPS_HOST is correct IP/domain
- [ ] VPS_USER can SSH and run Docker
- [ ] VPS_SSH_KEY is the PRIVATE key (not public)
- [ ] DEPLOY_PATH matches actual directory on VPS
- [ ] `.env` file exists on VPS with correct values
- [ ] Port 80 and 443 are open on VPS firewall

Common fixes:

**Permission denied (publickey):**
```bash
# On VPS
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Docker permission denied:**
```bash
# On VPS as root
sudo usermod -aG docker deploy
# Log out and back in
```

**Env file not found:**
```bash
# On VPS
cd /opt/ihsane-platform
cp .env.prod.example .env
nano .env  # Edit values
```

---

## Success! 🎉

When this checklist is complete:

- ✅ Push to main → Auto-deploys to VPS
- ✅ Tests run before deployment
- ✅ Health check verifies it's working
- ✅ Site live at https://ihsan-dz.duckdns.org

---

**Reference Documents:**
- Detailed Guide: `GITHUB_SECRETS_SETUP.md`
- CI/CD Setup: `CI_CD_SETUP.md`
- Deployment: `DEPLOY.md`

**Need Help?**
Check logs at: GitHub → Actions → Click failed workflow
