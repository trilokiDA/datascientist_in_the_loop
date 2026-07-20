# Quick Guide: Push to EPAM GitLab

## 🚀 Fastest Method (Automated Script)

### Option 1: Run PowerShell Script

```powershell
# Just run this script - it handles everything!
.\push_to_epam.ps1
```

The script will:
1. ✅ Check your current repository
2. ✅ Add EPAM remote
3. ✅ Check for uncommitted changes
4. ✅ Push to EPAM GitLab
5. ✅ Verify success

---

## ⚡ Manual Method (3 Commands)

If you prefer manual control:

```bash
# 1. Add EPAM remote
git remote add epam https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git

# 2. Push your code
git push epam main

# 3. Visit repository
# https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop
```

**Done!** Your code is now on EPAM GitLab with full commit history! 🎉

---

## 🔐 Authentication

You'll be asked for:
- **Username**: Your EPAM email
- **Password**: EPAM GitLab password or Personal Access Token

### Create Personal Access Token (Recommended)

1. Visit: https://git.garage.epam.com/-/profile/personal_access_tokens
2. Click "Add new token"
3. Name: "Claude Code Push"
4. Scopes: Check `write_repository`
5. Click "Create personal access token"
6. Copy the token
7. Use it as your password when pushing

---

## ❓ Troubleshooting

### "Permission denied"
→ You need write access to the repository. Ask the repository admin to add you.

### "Repository not found"
→ Verify the repository exists at the URL and you have access.

### "Authentication failed"
→ Use a Personal Access Token instead of your password (see above).

---

## 📖 Detailed Documentation

For complete details, troubleshooting, and alternative methods:
→ See `docs/GIT_MIGRATION_GUIDE.md`

---

## ✅ Verify Upload

After pushing, visit:
https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop

Check:
- ✅ All your files are there
- ✅ Commit history is visible
- ✅ README displays correctly

---

**That's all you need!** 🚀
