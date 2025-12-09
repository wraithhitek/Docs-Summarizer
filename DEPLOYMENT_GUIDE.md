# 🚀 Deployment Guide

## Why Not Netlify?

**Netlify only hosts static websites** (HTML, CSS, JavaScript). Your Content Summarizer is a **Flask backend application** that needs a Python server, so Netlify won't work.

---

## ✅ Recommended: Deploy to Render.com (FREE)

Render.com is perfect for Flask apps and has a generous free tier!

### Step-by-Step Deployment:

#### 1. **Prepare Your Code**

Make sure you have these files (already created):
- ✅ `render.yaml` - Render configuration
- ✅ `requirements-deploy.txt` - Python dependencies
- ✅ `.gitignore` - Files to ignore in Git
- ✅ `app.py` - Your Flask application

#### 2. **Create a GitHub Repository**

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Content Summarizer"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/content-summarizer.git
git branch -M main
git push -u origin main
```

#### 3. **Deploy to Render**

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your `content-summarizer` repository
5. Render will auto-detect the `render.yaml` file
6. Click **"Apply"**

#### 4. **Add Environment Variables**

In Render dashboard:
1. Go to your service → **"Environment"**
2. Add your API key:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyBTKzJFVXeKnStq25JDdmAXSNBnc2cf5m4`
3. Click **"Save Changes"**

#### 5. **Deploy!**

Render will automatically:
- Install dependencies
- Start your app
- Give you a URL like: `https://content-summarizer-xxxx.onrender.com`

**Done!** Your app is live! 🎉

---

## 🔄 Alternative Options

### Option 2: Railway.app

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Add environment variable `GEMINI_API_KEY`
6. Deploy!

**Pros:**
- Very simple
- $5 free credit
- Fast deployment

**Cons:**
- Free credit runs out eventually

---

### Option 3: PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account
3. Upload your code via Files tab
4. Create a new web app (Flask)
5. Configure WSGI file
6. Add environment variables in `.env`

**Pros:**
- Good for learning
- Free tier available

**Cons:**
- More manual setup
- Limited resources on free tier

---

### Option 4: Vercel (with Serverless Functions)

Vercel can host Flask apps using serverless functions, but requires restructuring your app.

**Not recommended for beginners** - stick with Render or Railway.

---

## 📝 Quick Commands Reference

### For Render/Railway (Git-based deployment):

```bash
# First time setup
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_URL
git push -u origin main

# Future updates
git add .
git commit -m "Update: description of changes"
git push
```

After pushing, Render/Railway will **auto-deploy** your changes!

---

## 🔐 Important: Environment Variables

Never commit your `.env` file to GitHub! It contains your API key.

The `.gitignore` file (already created) prevents this.

On Render/Railway, add environment variables through their dashboard:
- `GEMINI_API_KEY` - Your API key
- `GEMINI_MODEL_ID` - gemini-flash-latest
- `MAX_TOKENS` - 1024
- `TEMPERATURE` - 0.5

---

## 🐛 Troubleshooting

### Build Failed
- Check `requirements-deploy.txt` has all dependencies
- Check Python version (should be 3.11)

### App Crashes on Start
- Check logs in Render dashboard
- Verify environment variables are set
- Make sure `gunicorn` is in requirements

### Database Issues
- SQLite works on Render but data resets on redeploy
- For persistent data, upgrade to PostgreSQL (free on Render)

### API Key Not Working
- Double-check the environment variable name
- Make sure there are no extra spaces
- Redeploy after adding variables

---

## 📊 Monitoring Your Deployment

### Render Dashboard:
- View logs in real-time
- Monitor CPU/memory usage
- See deployment history
- Check uptime

### Free Tier Limits:
- **Render**: 750 hours/month (enough for 24/7)
- **Railway**: $5 credit (lasts ~1 month)
- **PythonAnywhere**: Limited CPU seconds

---

## 🎯 Recommended: Use Render.com

For your industrial training project, I recommend **Render.com** because:

✅ Completely free
✅ Easy to use
✅ Auto-deploys from GitHub
✅ Good for portfolio projects
✅ Professional deployment experience

---

## 📚 Next Steps After Deployment

1. **Test your live app** thoroughly
2. **Share the URL** in your project report
3. **Add the URL to your GitHub README**
4. **Take screenshots** for documentation
5. **Monitor usage** and fix any issues

---

## 🎓 For Your Industrial Training Report

Include these sections:

### Deployment Section:
- Platform used (Render.com)
- Deployment process
- Configuration details
- Live URL
- Screenshots of deployed app

### Technical Details:
- Server: Gunicorn WSGI server
- Platform: Render.com
- Database: SQLite (or PostgreSQL)
- Environment: Production

This shows you understand:
- Version control (Git)
- Cloud deployment
- Environment configuration
- Production best practices

Good luck with your deployment! 🚀
