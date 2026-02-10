# Deployment Guide

This guide covers how to deploy the **Chemical Equipment Visualizer** to the web.

## 1. Where to Deploy? (Recommended Free Tier Strategy)

For a project like this, I recommend the following split:
- **Backend (Django)**: **Render** (Free tier available, easy Python support) or **Railway** (Trial available).
- **Frontend (React)**: **Vercel** or **Netlify** (Both excellent free tiers).
- **Database**: **Render PostgreSQL** (Free tier) or stay with **SQLite** (Not recommended for production, but easiest for demos).

---

## 2. Preparing for Deployment

### A. Backend Preparation
1.  **Install `gunicorn`**: Production server for Django.
    ```bash
    pip install gunicorn psycopg2-binary
    pip freeze > requirements.txt
    ```
2.  **Create `Procfile`** (for Render):
    Create a file named `Procfile` (no extension) in `backend/`:
    ```
    web: gunicorn config.wsgi
    ```
3.  **Update `settings.py` for Production**:
    -   Set `DEBUG = False`.
    -   Set `ALLOWED_HOSTS = ['your-app-name.onrender.com', 'localhost']`.
    -   Configure Database to use `dj_database_url` if using PostgreSQL.

### B. Frontend Preparation
1.  **Update API URL**:
    Change `web_frontend/src/api.js` to point to your **live backend URL** instead of `localhost:8000`.
    ```javascript
    baseURL: 'https://your-django-app.onrender.com/api/',
    ```
2.  **Build Command**:
    Vercel/Netlify will use: `npm install && npm run build`.

---

## 3. Step-by-Step Deployment

### Step 1: Push Code to GitHub
Ensure your code is on GitHub.
-   repo/
    -   `backend/`
    -   `web_frontend/`
    -   `desktop_frontend/`

### Step 2: Deploy Backend to Render
1.  Sign up at [render.com](https://render.com).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repo.
4.  **Root Directory**: `backend`
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn config.wsgi`
7.  Click **Deploy**.

### Step 3: Deploy Frontend to Vercel
1.  Sign up at [vercel.com](https://vercel.com).
2.  **Add New Project** -> Import your GitHub repo.
3.  **Root Directory**: Click "Edit" and select `web_frontend`.
4.  **Build Command**: Default (`npm run build`) is fine.
5.  **Output Directory**: `dist` (Vite default).
6.  Click **Deploy**.

### Step 4: Desktop Application Distribution
The desktop app cannot be "hosted" like a website. Users must download it.
1.  **Package it**: Use `PyInstaller` to create a single `.exe` file.
    ```bash
    pip install pyinstaller
    pyinstaller --onefile --windowed main.py
    ```
2.  **Distribute**: Upload the `dist/main.exe` to Google Drive or GitHub Releases and share the link.
3.  **Note**: You must hardcode the **live backend URL** in `api_client.py` before building the exe.
