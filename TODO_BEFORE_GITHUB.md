# TODO Before Uploading to GitHub

Complete checklist before pushing your project to GitHub.

## ✅ Critical Tasks

### 1. Verify .env File
```bash
# Open .env and make sure it contains ONLY placeholders:
DISCORD_TOKEN=your_discord_token_here
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

**⚠️ NEVER commit your real tokens!**

### 2. Test .gitignore
```bash
git status
```

Make sure `.env` is NOT listed in the output. It should be ignored.

### 3. Remove FFmpeg Binary (Optional)
```bash
# FFmpeg is large and users can install it themselves
# If you want to remove it:
rm ffmpeg.exe  # Windows
rm ffmpeg      # Linux/Mac
```

It's in `.gitignore` so it won't be committed anyway.

### 4. Clean Python Cache
```bash
# Remove __pycache__ directories
find . -type d -name __pycache__ -exec rm -r {} +

# Or on Windows:
# Delete __pycache__ folders manually
```

---

## 📝 Recommended Tasks

### 5. Update README.md
Replace `YOUR_USERNAME` with your actual GitHub username:
```markdown
git clone https://github.com/YOUR_USERNAME/discord-music-bot.git
```

### 6. Add Your Information
In `LICENSE` file, update the copyright year if needed:
```
Copyright (c) 2024 Your Name
```

### 7. Test the Bot
Make sure everything works:
```bash
python bot.py
```

Test these commands:
- `!play test song`
- `!queue`
- `!skip`
- `!playlist_save test`
- `!playlist_list`

---

## 🔍 Verification Checklist

### Files to Check

- [ ] `.env` contains only placeholders
- [ ] `.env.example` is correct
- [ ] `.gitignore` is configured
- [ ] `README.md` is complete
- [ ] All documentation is in English
- [ ] No personal information in code
- [ ] No real tokens anywhere
- [ ] LICENSE file is present

### Code Quality

- [ ] All files use English
- [ ] Comments are clear
- [ ] No debug print statements
- [ ] No hardcoded values
- [ ] Error handling is present

### Documentation

- [ ] README.md is complete
- [ ] QUICK_START.md is accurate
- [ ] All docs/ files are present
- [ ] Examples are working
- [ ] Links are correct

---

## 🚀 Ready to Upload?

### Step 1: Initialize Git
```bash
git init
```

### Step 2: Add Files
```bash
git add .
```

### Step 3: Check Status
```bash
git status
```

**Verify:**
- `.env` is NOT listed (should be ignored)
- All other files are listed
- No sensitive data

### Step 4: Commit
```bash
git commit -m "Initial commit: Discord Music Bot v2.0"
```

### Step 5: Create GitHub Repository
1. Go to https://github.com/new
2. Name: `discord-music-bot`
3. Description: `A feature-rich Discord music bot with YouTube and Spotify support`
4. Public or Private (your choice)
5. Don't initialize with README
6. Create repository

### Step 6: Add Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/discord-music-bot.git
```

Replace `YOUR_USERNAME` with your GitHub username!

### Step 7: Push
```bash
git branch -M main
git push -u origin main
```

---

## 🎉 After Upload

### 1. Add Repository Details

In GitHub repository settings:
- **Description:** A feature-rich Discord music bot with YouTube and Spotify support
- **Website:** (optional)
- **Topics:** discord, discord-bot, music-bot, python, youtube, spotify, discord-py

### 2. Enable Features
- ✅ Issues
- ✅ Discussions (optional)
- ✅ Projects (optional)

### 3. Create First Release
1. Go to "Releases"
2. Click "Create a new release"
3. Tag: `v2.0.0`
4. Title: `Version 2.0.0`
5. Description: Copy from CHANGELOG.md
6. Publish

### 4. Update README Badges
Replace `YOUR_USERNAME` in badges:
```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/discord-music-bot)
```

---

## ⚠️ Common Mistakes to Avoid

### DON'T:
- ❌ Commit `.env` file with real tokens
- ❌ Include `ffmpeg.exe` in repository
- ❌ Leave Spanish text in code/docs
- ❌ Forget to test before pushing
- ❌ Use real tokens in examples

### DO:
- ✅ Use `.env.example` for templates
- ✅ Test everything before pushing
- ✅ Keep documentation updated
- ✅ Use meaningful commit messages
- ✅ Check .gitignore is working

---

## 🔒 Security Check

### Before Pushing, Verify:

1. **No Real Tokens**
```bash
grep -r "MTI" .  # Discord tokens start with MTI
grep -r "DISCORD_TOKEN=" .env
```

If you find real tokens, remove them!

2. **No API Keys**
```bash
grep -r "client_id" .
grep -r "client_secret" .
```

Make sure only placeholders exist.

3. **Check .gitignore**
```bash
cat .gitignore
```

Should include:
- `.env`
- `__pycache__/`
- `.venv/`
- `ffmpeg.exe`

---

## 📋 Final Checklist

Before running `git push`:

- [ ] Tested bot locally
- [ ] All documentation in English
- [ ] No sensitive data in files
- [ ] .gitignore is working
- [ ] README.md is complete
- [ ] LICENSE is present
- [ ] .env contains only placeholders
- [ ] All links are correct
- [ ] Code is clean and commented
- [ ] Examples are working

---

## 🎯 Quick Commands

```bash
# 1. Check what will be committed
git status

# 2. If .env appears, STOP! Fix .gitignore
# Otherwise, continue:

# 3. Add all files
git add .

# 4. Commit
git commit -m "Initial commit: Discord Music Bot v2.0"

# 5. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/discord-music-bot.git

# 6. Push
git branch -M main
git push -u origin main
```

---

## 🆘 If Something Goes Wrong

### Committed .env by Mistake?

1. Remove from Git:
```bash
git rm --cached .env
git commit -m "Remove .env from repository"
```

2. Regenerate your Discord token immediately!

3. Push:
```bash
git push
```

### Wrong Files Committed?

```bash
git reset HEAD~1  # Undo last commit
# Fix the issue
git add .
git commit -m "Fixed commit"
```

---

## ✅ You're Ready!

Once you've completed this checklist:
1. Your project is secure
2. Your code is clean
3. Your documentation is complete
4. You're ready to share with the world

**Good luck with your GitHub upload!** 🚀

---

## 📞 Need Help?

- Review GITHUB_SETUP.md for detailed instructions
- Check PROJECT_SUMMARY.md for project overview
- Read QUICK_START.md to verify setup

**Remember:** Never commit sensitive data! 🔒
