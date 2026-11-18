# IAFS Deployment Guide

This guide walks you through deploying **IAFS (Intelligent Adaptive Feedback System)** using the recommended cloud split architecture:
- **Frontend**: [Vercel](https://vercel.com/) (Fast CDN, automatic HTTPS, SPA rewrites)
- **Backend**: [Render](https://render.com/) or [Railway](https://railway.app/) (Python 3 + Gunicorn WSGI)
- **Database**: [MongoDB Atlas](https://www.mongodb.com/atlas) (Managed cloud MongoDB)

---

## 1. MongoDB Atlas Setup (Database)

1. Sign in to your [MongoDB Atlas](https://cloud.mongodb.com/) account.
2. In your Cluster, click **Connect** > **Drivers** (Python).
3. Copy your connection string, which looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your database user password and ensure Network Access (`0.0.0.0/0`) is enabled so Render/Railway can connect.

---

## 2. Backend Deployment (Render or Railway)

### Option A: Deploy on Render (Recommended)

1. Push your latest code to your GitHub repository:
   ```bash
   git add .
   git commit -m "Configure production deployment"
   git push origin main
   ```
2. Go to [Render Dashboard](https://dashboard.render.com/) > **New +** > **Web Service**.
3. Connect your GitHub repository `PrinceSinghdoya/IAFS`.
4. Configure the settings:
   - **Name**: `iafs-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app`
5. In **Environment Variables**, add:
   | Key | Value | Description |
   |---|---|---|
   | `MONGO_URI` | `mongodb+srv://...` | Your MongoDB Atlas connection URI |
   | `DB_NAME` | `iafs` | Database name |
   | `JWT_SECRET` | *(Random 32+ character string)* | Secret for auth tokens |
   | `CORS_ORIGINS` | `*` *(or your Vercel URL)* | Allowed frontend origins |
   | `AUTO_SEED` | `true` | Populates demo data & curriculum on first run |
   | `TEACHER_INVITE_CODE` | `IAFS2026` | Code required to register teacher accounts |
6. Click **Create Web Service**. Once deployed, copy your backend URL:
   `https://iafs-backend.onrender.com`

---

## 3. Frontend Deployment (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Import your GitHub repository `PrinceSinghdoya/IAFS`.
3. In the project configuration:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://iafs-backend.onrender.com` *(your backend URL)* |
5. Click **Deploy**.

---

## 4. Verification & Testing

Once both services are live:
1. Visit your Vercel URL (e.g. `https://iafs-frontend.vercel.app/`).
2. Test health check at: `https://your-backend.onrender.com/api/health`
3. Sign in using any seeded demo accounts:
   - **Admin**: `admin@iafs.school` / `Admin@123`
   - **Teacher**: `teacher@iafs.school` / `Teacher@123`
   - **Student (Class 4)**: `aarav@iafs.school` / `Student@123`
   - **Student (Class 8)**: `priya@iafs.school` / `Student@123`
