# Git Migration Guide - Upload to EPAM GitLab

## Overview
This guide shows how to upload your current repository (with all commit history) to the EPAM GitLab repository.

**Target Repository**: `https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop`

## Prerequisites

1. **Git installed** on your machine
2. **Access to EPAM GitLab** with write permissions
3. **Current repository** has commits to push

## Method 1: Add Remote and Push (Recommended)

This method preserves all your commit history.

### Step 1: Check Current Remotes

```bash
# See what remotes you currently have
git remote -v
```

You'll see something like:
```
origin  <current-remote-url> (fetch)
origin  <current-remote-url> (push)
```

### Step 2: Add EPAM GitLab as Remote

```bash
# Add the EPAM GitLab repository as a new remote called 'epam'
git remote add epam https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git
```

### Step 3: Verify Remote Added

```bash
git remote -v
```

Now you should see:
```
origin  <current-remote-url> (fetch)
origin  <current-remote-url> (push)
epam    https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git (fetch)
epam    https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git (push)
```

### Step 4: Push to EPAM GitLab

```bash
# Push your main branch to EPAM GitLab
git push epam main

# If your branch is named 'master' instead:
# git push epam master

# Push all branches (optional)
# git push epam --all

# Push all tags (optional)
# git push epam --tags
```

### Step 5: Authenticate

You'll be prompted for credentials:
- **Username**: Your EPAM email or GitLab username
- **Password**: Your EPAM GitLab password or Personal Access Token

**Note**: If using 2FA, you'll need to create a Personal Access Token:
1. Go to: `https://git.garage.epam.com/-/profile/personal_access_tokens`
2. Create token with `write_repository` scope
3. Use token as password

### Step 6: Verify Upload

Visit: `https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop`

You should see all your code and commit history!

---

## Method 2: Change Origin Remote

If you want to switch completely to EPAM GitLab (and stop using the old remote):

### Step 1: Remove Current Origin

```bash
git remote remove origin
```

### Step 2: Add EPAM as New Origin

```bash
git remote add origin https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git
```

### Step 3: Push All Branches

```bash
# Push main branch and set upstream
git push -u origin main

# Push all branches
git push origin --all

# Push all tags
git push origin --tags
```

---

## Method 3: Fresh Start (No History)

If you DON'T need the git history and want a clean start:

### Step 1: Initialize Empty EPAM Repo

1. Go to: `https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop`
2. Follow GitLab's instructions to initialize

### Step 2: Remove Git History Locally

```bash
# Remove .git folder (CAUTION: This deletes all history!)
rm -rf .git

# Initialize new git repo
git init
```

### Step 3: Add EPAM Remote

```bash
git remote add origin https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git
```

### Step 4: Commit and Push

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: EDA Pipeline v3.1"

# Push to EPAM
git push -u origin main
```

---

## Complete PowerShell Script (Windows)

Here's a complete script you can run:

```powershell
# Navigate to your project directory
cd C:\Users\TrilokiGupta\Desktop\Work\claudeCode\test

# Check current status
Write-Host "Current remotes:" -ForegroundColor Cyan
git remote -v

# Add EPAM remote
Write-Host "`nAdding EPAM GitLab remote..." -ForegroundColor Cyan
git remote add epam https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git

# Verify
Write-Host "`nRemotes after adding:" -ForegroundColor Cyan
git remote -v

# Show current branch
Write-Host "`nCurrent branch:" -ForegroundColor Cyan
git branch

# Push to EPAM
Write-Host "`nPushing to EPAM GitLab..." -ForegroundColor Yellow
Write-Host "You will be prompted for credentials" -ForegroundColor Yellow
git push epam main

Write-Host "`n✅ Done! Check your repository at:" -ForegroundColor Green
Write-Host "https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop" -ForegroundColor Green
```

Save as `push_to_epam.ps1` and run: `.\push_to_epam.ps1`

---

## Troubleshooting

### Issue: "Repository not found"

**Cause**: Repository doesn't exist on EPAM GitLab or you don't have access.

**Solution**:
1. Ensure the repository exists at the URL
2. Check you have write permissions
3. Verify the URL is correct

### Issue: "Authentication failed"

**Cause**: Incorrect credentials or 2FA enabled.

**Solution**:
1. Create a Personal Access Token (see Step 5 above)
2. Use token as password
3. Or check username/password

### Issue: "Permission denied"

**Cause**: You don't have write access to the repository.

**Solution**:
1. Ask repository owner/admin to add you
2. Ensure you have "Developer" or "Maintainer" role

### Issue: "Updates were rejected"

**Cause**: Remote repository already has content that you don't have locally.

**Solution**:
```bash
# Pull and merge first
git pull epam main --allow-unrelated-histories

# Then push
git push epam main
```

### Issue: "The requested URL returned error: 403"

**Cause**: Access forbidden - authentication issue.

**Solution**:
1. Ensure you're logged into EPAM GitLab
2. Check repository visibility (should be accessible to you)
3. Use Personal Access Token

---

## What Gets Pushed

When you push with history:

✅ **Included:**
- All commit history
- All branches (if you use `--all`)
- All tags (if you use `--tags`)
- Current code state
- Commit messages
- Author information

❌ **Not Included:**
- Local `.env` files (ignored by .gitignore)
- `node_modules/`, `.venv/` (ignored)
- Local configuration files (ignored)
- Uncommitted changes (use `git add` and `git commit` first)

---

## Before Pushing Checklist

- [ ] Committed all changes (`git status` shows clean)
- [ ] Removed sensitive information (API keys, passwords)
- [ ] Updated README.md
- [ ] Added .gitignore for sensitive files
- [ ] Tested the application works
- [ ] Documented any setup steps

---

## After Pushing

### 1. Verify on GitLab
Visit: `https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop`

Check:
- ✅ All files present
- ✅ Commit history visible
- ✅ README displays correctly
- ✅ No sensitive data exposed

### 2. Update Local Remote (Optional)

If you want to make EPAM the default remote:

```bash
# Set EPAM as upstream for current branch
git branch --set-upstream-to=epam/main main

# Or rename remote
git remote rename epam origin
```

### 3. Clone Fresh Copy (Verify)

```bash
# Clone from EPAM to verify everything worked
git clone https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git test-clone

cd test-clone

# Verify commit history
git log --oneline

# Verify files
ls
```

---

## Security Notes

### ⚠️ Before Pushing - Check for Secrets

```bash
# Search for potential API keys
git log -p | grep -i "api_key\|password\|secret\|token"

# Check current files
grep -r "GROQ_API_KEY" . --exclude-dir=.git
```

### 🔒 Ensure .env is Ignored

Your `.gitignore` should include:
```
.env
.env.local
*.key
*.pem
secrets/
```

### 🛡️ Use Environment Variables

Never commit:
- API keys
- Passwords
- Database credentials
- SSH keys
- Personal tokens

Use `.env.example` instead:
```env
GROQ_API_KEY=your_api_key_here
```

---

## Summary

**Recommended Command Sequence:**

```bash
# Add remote
git remote add epam https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git

# Push main branch
git push epam main

# Push all branches (optional)
git push epam --all

# Push tags (optional)  
git push epam --tags
```

**That's it!** Your code and history are now on EPAM GitLab! 🚀
