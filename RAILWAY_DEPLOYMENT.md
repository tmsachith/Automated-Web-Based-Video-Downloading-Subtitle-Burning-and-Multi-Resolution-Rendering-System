# 🚂 Railway Deployment Guide - Step by Step

Deploy your video processing system to Railway for FREE in under 10 minutes!

---

## 📋 Prerequisites (5 minutes)

### 1. Create Accounts (Free)

**GitHub Account:**
- Go to: https://github.com/signup
- Sign up with your email
- Verify your email

**Railway Account:**
- Go to: https://railway.app/
- Click "Login" → "Login with GitHub"
- Authorize Railway to access your GitHub

**You get FREE:**
- $5 credit per month
- 500 execution hours
- Perfect for testing and personal use

---

## 🎯 Step-by-Step Deployment

### STEP 1: Initialize Git Repository (2 minutes)

Open PowerShell in your project directory and run:

```powershell
# Navigate to project directory (if not already there)
cd "d:\Projects\Automated Web-Based Video Downloading, Subtitle Integration, and Multi-Resolution Rendering System"

# Initialize git
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit - Video Processing System"
```

**Expected output:**
```
Initialized empty Git repository...
[main (root-commit) abc1234] Initial commit - Video Processing System
 22 files changed, 2000+ insertions(+)
```

---

### STEP 2: Create GitHub Repository (3 minutes)

**Option A: Using GitHub Website (Recommended)**

1. Go to: https://github.com/new
2. Repository name: `video-processing-system`
3. Description: `Automated video processing with subtitle integration`
4. Select: **Public** (required for free deployment)
5. **DON'T** check "Initialize with README"
6. Click "Create repository"

**Option B: Using GitHub CLI (if installed)**

```powershell
gh repo create video-processing-system --public --source=. --remote=origin
```

---

### STEP 3: Push Code to GitHub (1 minute)

```powershell
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/video-processing-system.git

# Push code
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password)
  - Generate at: https://github.com/settings/tokens
  - Select: `repo` scope
  - Copy the token and paste it

---

### STEP 4: Deploy to Railway (2 minutes)

1. **Go to Railway Dashboard:**
   - Visit: https://railway.app/dashboard

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway (if prompted)

3. **Select Your Repository:**
   - Find: `video-processing-system`
   - Click on it

4. **Railway Auto-Detects:**
   - Language: Python
   - Buildpack: Nixpacks
   - Start command: `python web_app.py`

5. **Click "Deploy"**
   - Railway starts building...
   - Wait 2-3 minutes for first deployment

---

### STEP 5: Install FFmpeg Buildpack (CRITICAL!)

**This is required for video processing to work!**

1. **In Railway Dashboard:**
   - Click on your deployed service
   - Go to "Settings" tab

2. **Add Buildpack:**
   - Scroll to "Environment" section
   - Click "Add Variable"
   - Add these one by one:

   ```
   Name: NIXPACKS_APT_PKGS
   Value: ffmpeg
   ```

3. **Redeploy:**
   - Go to "Deployments" tab
   - Click "⋮" (three dots) on latest deployment
   - Click "Redeploy"

---

### STEP 6: Configure Environment Variables (1 minute)

1. **In Railway Settings:**
   - Click "Variables" tab
   - Add these variables:

```
PORT = 5000
FLASK_ENV = production
HOST = 0.0.0.0
```

2. **Click "Save" (automatic redeploy)**

---

### STEP 7: Get Your Public URL (30 seconds)

1. **Generate Domain:**
   - In Railway dashboard
   - Click "Settings" tab
   - Under "Networking" section
   - Click "Generate Domain"

2. **Your URL will be:**
   ```
   https://video-processing-system-production.up.railway.app
   ```

3. **Click the URL to open your app!**

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] URL loads successfully
- [ ] Web interface displays correctly
- [ ] Can submit a test job
- [ ] FFmpeg is working (check logs)
- [ ] Processing completes successfully

---

## 🔧 Troubleshooting

### Issue 1: "Application Failed to Start"

**Check Logs:**
```
Railway Dashboard → Deployments → Click on deployment → View Logs
```

**Common fixes:**
- Verify `requirements.txt` has all packages
- Check `Procfile` has correct command
- Ensure FFmpeg buildpack is installed

### Issue 2: "FFmpeg Not Found"

**Solution:**
```
1. Settings → Variables → Add:
   NIXPACKS_APT_PKGS = ffmpeg

2. Redeploy the application
```

### Issue 3: Build Fails

**Check:**
- Python version in `runtime.txt` (should be 3.10.0 or 3.11.0)
- All files committed to Git
- GitHub repository is public

### Issue 4: "Out of Memory"

**Solution - Optimize config.py:**
```python
PROCESSING_CONFIG = {
    'parallel_encoding': False,  # Sequential processing
    'cleanup_temp_files': True,   # Clean immediately
}

# Process fewer resolutions by default
RESOLUTIONS = {
    '480p': {...},
    '720p': {...}
}
```

---

## 💰 Free Tier Limits

**Railway Free Tier:**
- ✅ $5 credit per month
- ✅ ~500 hours of usage
- ✅ 1GB RAM
- ✅ 1GB disk storage
- ✅ Unlimited bandwidth

**What this means:**
- Process ~50-100 short videos per month
- App sleeps when inactive (saves hours)
- Perfect for personal use!

**Tips to stay within limits:**
- Process smaller videos
- Use 1-2 resolutions instead of all 4
- Let app sleep when not in use
- Monitor usage in Railway dashboard

---

## 📊 Monitor Your Deployment

### View Logs (Real-time)
```
Railway Dashboard → Your Service → Deployments → View Logs
```

### Check Resource Usage
```
Railway Dashboard → Metrics
```
Shows:
- CPU usage
- Memory usage
- Network traffic
- Build time

### View Build Status
```
Railway Dashboard → Deployments
```
See:
- Build logs
- Deploy time
- Git commit details

---

## 🔄 Update Your Deployment

When you make code changes:

```powershell
# Make your changes, then:
git add .
git commit -m "Description of changes"
git push origin main
```

**Railway auto-deploys** within 1-2 minutes!

---

## 🎯 Complete Deployment Commands (Summary)

```powershell
# 1. Initialize Git
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repo (via website: github.com/new)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/video-processing-system.git
git branch -M main
git push -u origin main

# 3. Deploy on Railway (via website: railway.app)
# - New Project → Deploy from GitHub
# - Select your repository
# - Click Deploy

# 4. Add FFmpeg
# Railway Settings → Variables → Add:
# NIXPACKS_APT_PKGS = ffmpeg

# 5. Generate domain
# Railway Settings → Networking → Generate Domain

# Done! 🎉
```

---

## 🚀 Your App is Live!

Access your video processing system at:
```
https://your-app-name.up.railway.app
```

**Features available:**
- ✅ Web interface for job submission
- ✅ Real-time processing status
- ✅ Download processed videos
- ✅ Multi-resolution encoding
- ✅ Subtitle integration

---

## 📱 Share Your App

Your Railway URL is public! You can:
- Share with friends/family
- Use from any device
- Access from anywhere
- No local setup needed

**Security Note:** 
- Consider adding authentication for production
- Don't share URLs publicly if processing sensitive content
- Monitor your Railway usage

---

## 🛡️ Optional: Add Basic Authentication

Create `auth_middleware.py`:

```python
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'your-secure-password'

def authenticate():
    return Response(
        'Login required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
```

Then in `web_app.py`, add `@requires_auth` decorator to routes.

---

## 🎓 What You've Accomplished

✅ Deployed a full-stack web application
✅ Set up continuous deployment (auto-updates)
✅ Configured cloud infrastructure
✅ Made your app accessible worldwide
✅ All on Railway's free tier!

---

## 📞 Need Help?

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/
- Status: https://status.railway.app/

**GitHub Issues:**
- Check your repository's Issues tab
- Railway community forums

**Logs:**
- Always check Railway logs first
- Look for error messages
- Search errors online

---

## 🎉 Success!

Your video processing system is now:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Automatically updated
- ✅ Running on free cloud infrastructure

**Start processing videos at:**
```
https://your-railway-app.up.railway.app
```

---

*Happy video processing! 🎬*
