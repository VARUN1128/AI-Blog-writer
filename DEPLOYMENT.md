# Deployment Guide for AI Blog Generator

This guide will help you deploy your AI Blog Generator app to various platforms.

## Option 1: Render (Recommended - Easiest & Free)

### Steps:

1. **Create a GitHub Repository**
   - Push your code to GitHub (make sure `.env` is in `.gitignore`)
   - Don't commit your `.env` file with the API key

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `ai-blog-generator` (or any name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variable:
     - **Key**: `GEMINI_API_KEY`
     - **Value**: Your Gemini API key (paste it here)
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

### Note: Render free tier spins down after 15 minutes of inactivity, so first request may be slow.

---

## Option 2: Railway (Also Easy & Free)

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app) and sign up/login
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python
   - Add Environment Variable:
     - Click on your service → "Variables"
     - Add: `GEMINI_API_KEY` = your API key
   - Railway will automatically deploy
   - Your app will be live at: `https://your-app-name.up.railway.app`

---

## Option 3: Fly.io (Good Free Tier)

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Initialize Fly.io**
   ```bash
   fly launch
   ```
   - Follow the prompts
   - Don't deploy yet when asked

4. **Set Environment Variable**
   ```bash
   fly secrets set GEMINI_API_KEY=your_api_key_here
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

---

## Option 4: PythonAnywhere (Simple for Python)

### Steps:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload your files**
   - Go to "Files" tab
   - Upload all your project files (except `.env`)

3. **Install dependencies**
   - Go to "Consoles" → "Bash"
   - Run: `pip3.10 install --user -r requirements.txt`

4. **Set up Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Manual configuration" → "Python 3.10"
   - In WSGI file, add:
   ```python
   import sys
   path = '/home/yourusername/ai-blog-generator'
   if path not in sys.path:
       sys.path.append(path)
   
   from main import app
   application = app
   ```

5. **Set Environment Variable**
   - In "Web" tab → "Environment variables"
   - Add: `GEMINI_API_KEY` = your API key

6. **Reload** your web app

---

## Important Notes for All Platforms:

### 1. **Never commit `.env` file**
   - Make sure `.env` is in `.gitignore`
   - Add environment variables through the platform's dashboard

### 2. **Update `main.py` for production** (if needed)
   - The current code should work, but you might want to add:
   ```python
   # At the end of main.py
   if __name__ == "__main__":
       import uvicorn
       port = int(os.getenv("PORT", 8000))
       uvicorn.run(app, host="0.0.0.0", port=port)
   ```

### 3. **Static Files**
   - Make sure `static/` and `templates/` folders are included in your repository

### 4. **Database/Storage**
   - Currently using JSON file storage
   - For production, consider using a database (PostgreSQL, SQLite, etc.)

---

## Quick Deploy Checklist:

- [ ] Code pushed to GitHub
- [ ] `.env` file NOT in repository (in `.gitignore`)
- [ ] `requirements.txt` is up to date
- [ ] Environment variable `GEMINI_API_KEY` set on platform
- [ ] Static files and templates included
- [ ] App deployed and accessible

---

## Recommended: Render.com

**Why Render?**
- ✅ Free tier available
- ✅ Easy setup (just connect GitHub)
- ✅ Automatic deployments
- ✅ Good for FastAPI apps
- ✅ Simple environment variable management

**Limitations:**
- Free tier spins down after inactivity (first request may be slow)
- Limited to 750 hours/month on free tier

---

## Need Help?

If you encounter issues:
1. Check the platform's logs/deployment logs
2. Verify environment variables are set correctly
3. Make sure all dependencies are in `requirements.txt`
4. Check that the start command is correct

