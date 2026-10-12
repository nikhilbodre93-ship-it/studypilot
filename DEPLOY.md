# 🚀 StudyPilot Permanent Free Cloud Deployment Guide

This guide walks you through deploying **StudyPilot** permanently and 100% free across reliable cloud providers:
* **Database**: **[Neon](https://neon.tech)** (Serverless PostgreSQL — free tier with no 30-day expiration)
* **Backend**: **[Render](https://render.com)** or **[Koyeb](https://koyeb.com)** (Docker Web Service)
* **Frontend**: **[Vercel](https://vercel.com)** (React + Vite SPA)
* **Keep-Alive**: **[UptimeRobot](https://uptimerobot.com)** (Free 5-minute health check monitor to prevent sleeping)

---

## 📋 Prerequisites & Secret Generation

### 1. Generate a Cryptographically Secure `SECRET_KEY`
Run this in PowerShell or bash:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
*Save the output securely — you will paste it into your backend environment variables.*

---

## 🛠️ Step 1: Push Your Code to GitHub

*(Antigravity has already prepared your `.gitignore` so no binaries, `.env` files, databases, or secrets will be committed).*

Run the following commands in your project root (`c:\Users\nikhi\studypilot`):

```bash
# 1. Initialize git
git init

# 2. Stage all clean project files
git add .

# 3. Verify staged files (ensure no .env, *.db, *.exe, *.zip are listed)
git status

# 4. Commit
git commit -m "Initial production-ready commit for StudyPilot"

# 5. Create a new repository on https://github.com/new (make it Public or Private)
# Then link and push:
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
git push -u origin main
```

---

## 🗄️ Step 2: Set Up Neon PostgreSQL (Free & Permanent)

Render's built-in free PostgreSQL expires after 30 days. Neon's free tier has **no expiration date** and provides 0.5 GB of storage.

1. Go to **[https://neon.tech](https://neon.tech)** and sign up / log in with GitHub.
2. Click **Create Project**:
   * **Project Name:** `studypilot`
   * **Postgres Version:** 16
   * **Region:** Select the region closest to you (e.g. US East or Europe).
3. On the project dashboard, find **Connection Details**:
   * Switch the dropdown to **`Parameters only`** or **`Connection string`**.
   * Copy the connection string. It will look like:
     ```text
     postgresql://neondb_owner:npg_abcdef123@ep-cool-forest-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
   *(Note: StudyPilot automatically converts `postgres://` to `postgresql://` if needed).*

---

## ⚙️ Step 3: Deploy the Backend on Render (or Koyeb)

### Option A: Deploy on Render (Recommended)
1. Go to **[https://dashboard.render.com](https://dashboard.render.com)**.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Fill in the settings:
   * **Name:** `studypilot-backend`
   * **Region:** Same general region as your Neon database (e.g. Oregon or Frankfurt).
   * **Language / Runtime:** **Docker**
   * **Dockerfile Path:** `./backend/Dockerfile`
   * **Docker Build Context:** `./backend`
   * **Instance Type:** **Free**
5. Scroll down to **Environment Variables** and add:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `ENVIRONMENT` | `production` | Production mode |
   | `DATABASE_URL` | *(Pasted from Neon)* | Your Neon PostgreSQL connection string |
   | `SECRET_KEY` | *(Generated earlier)* | 32+ character random secret string |
   | `BACKEND_CORS_ORIGINS` | `http://localhost:5173` | *(Temporary; you will update this after deploying the frontend)* |
   | `LLM_PROVIDER` | `mock` | High-quality offline mock, or `gemini` / `groq` |
   | `PORT` | `8000` | Backend port |
6. Under **Advanced**, set **Health Check Path** to:
   ```text
   /health
   ```
7. Click **Create Web Service**.
8. Render will build the Docker container and automatically run database migrations:
   ```bash
   alembic upgrade head
   ```
9. When deployment finishes, copy your backend URL (e.g. `https://studypilot-backend.onrender.com`).

---

## 🎨 Step 4: Deploy the Frontend on Vercel

1. Go to **[https://vercel.com](https://vercel.com)** and sign in with GitHub.
2. Click **Add New...** → **Project**.
3. Import your `studypilot` repository.
4. Configure the project:
   * **Framework Preset:** `Vite`
   * **Root Directory:** Click **Edit** and select **`frontend`**
   * **Build Command:** `npm run build`
   * **Output Directory:** `dist`
5. Expand **Environment Variables** and add:
   | Key | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://studypilot-backend.onrender.com` *(Your Render backend URL, without trailing slash)* |
6. Click **Deploy**.
7. Vercel will build and deploy the React application in ~45 seconds.
8. Copy your live Vercel URL (e.g. `https://studypilot.vercel.app`).

---

## 🔄 Step 5: Update CORS on the Backend

Now that you have your live Vercel URL:
1. Return to your **Render Dashboard** → `studypilot-backend` → **Environment**.
2. Edit `BACKEND_CORS_ORIGINS` and set it to:
   ```text
   https://studypilot.vercel.app,http://localhost:5173
   ```
   *(Replace `https://studypilot.vercel.app` with your actual Vercel URL).*
3. Click **Save Changes**. Render will automatically redeploy with the updated CORS configuration.

---

## ⏰ Step 6: Keep the Backend from Sleeping (UptimeRobot)

Render's free tier spins down after 15 minutes of inactivity. When a student visits, it takes ~50 seconds to wake up. To keep it warm 24/7:

1. Go to **[https://uptimerobot.com](https://uptimerobot.com)** (100% free account, up to 50 monitors).
2. Click **Add New Monitor**:
   * **Monitor Type:** `HTTP(s)`
   * **Friendly Name:** `StudyPilot Backend Health`
   * **URL (or IP):** `https://studypilot-backend.onrender.com/health`
   * **Monitoring Interval:** Every `5 minutes`
3. Click **Create Monitor**.
*UptimeRobot will ping the `/health` endpoint every 5 minutes, preventing Render from ever sleeping!*

---

## 👤 Step 7: Seed Initial Demo Data (Optional)

To populate the production database with sample subjects, topics, and the demo student:
1. In your local terminal, run the seed script with your Neon `DATABASE_URL`:
   ```bash
   cd backend
   $env:DATABASE_URL = "<PASTE_YOUR_NEON_DATABASE_URL>"
   .\.venv\Scripts\python app/seed.py
   ```
2. Demo credentials created:
   * **Email:** `demo@studypilot.io`
   * **Password:** `StudyPilot2026!`

---

## ⚡ Free-Tier Limitations & Summary

| Provider | Service | Free Tier Limits | Strategy |
| :--- | :--- | :--- | :--- |
| **Neon** | PostgreSQL | 0.5 GB storage, serverless compute | No expiration. Perfect for relational data & schemas. |
| **Render** | Backend Web Service | 512 MB RAM, 0.1 CPU, sleeps after 15m idle | Kept active 24/7 with UptimeRobot free 5-minute ping. |
| **Vercel** | Frontend SPA | 100 GB bandwidth / month, global CDN | Fast, automatic HTTPS, SPA rewrites configured. |
| **UptimeRobot** | Monitor | 50 monitors, 5-minute interval | Completely free forever. |
