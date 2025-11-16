# 🚀 Deploying H. pylori CDSS to Render

This guide explains how to deploy the H. pylori Clinical Decision Support System to Render.

## 📋 Prerequisites

- Render account (free tier works)
- GitHub repository with your code
- PostgreSQL database (Render provides free instances)

---

## 🔧 Backend Deployment (FastAPI)

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `hpylori-cdss-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `master` or `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables

Add these in Render's Environment tab:

```bash
# Required
DATABASE_URL=<Your Render PostgreSQL URL>
JWT_SECRET=<Generate a strong random secret>
ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
FRONTEND_URL=https://your-frontend-url.onrender.com

# Optional
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib
SCREEN_THRESH=0.60
```

**To generate a secure JWT_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Database Setup

1. Create a PostgreSQL database:
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `hpylori-cdss-db`
   - Free tier is fine for development

2. Copy the **Internal Database URL**

3. Paste it as `DATABASE_URL` in your backend service environment variables

---

## 🌐 Frontend Deployment (Static Site)

### Option A: Serve from FastAPI (Recommended)

Your FastAPI app already serves static files from the `ui/` directory.

- Frontend will be available at: `https://your-backend.onrender.com/`
- No separate frontend deployment needed!

### Option B: Separate Static Site

If you want to deploy frontend separately:

1. Create new **"Static Site"**
2. **Publish directory:** `ui`
3. No build command needed
4. Update `FRONTEND_URL` and `ALLOWED_ORIGINS` in backend to match this URL

---

## 🔐 Post-Deployment Setup

### 1. Create Admin User

After deployment, create your first admin user:

```bash
# Using Render Shell (from your service's "Shell" tab)
python -c "
from app.db import get_db, init_db
from app.models import User
from passlib.context import CryptContext

init_db()
db = next(get_db())

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
admin = User(
    username='admin',
    email='admin@yourdomain.com',
    password_hash=pwd_context.hash('YourSecurePassword123!'),
    full_name='System Administrator',
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('✅ Admin user created!')
"
```

### 2. Upload ML Models

Ensure your model files are in the repository:
- `models/screening_hp_pos_calibrated.joblib`
- `models/staging_3class.joblib`

If models are too large for Git, use Git LFS or upload manually via Render Shell.

---

## 🧪 Testing Your Deployment

### 1. Check Backend Health

```bash
curl https://your-backend.onrender.com/
# Should return: {"message": "H. pylori CDSS API is running"}
```

### 2. Test Login

```bash
curl -X POST https://your-backend.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YourSecurePassword123!"}'
```

### 3. Access Frontend

Open: `https://your-backend.onrender.com/login.html`

---

## 📊 Monitoring

### Logs

View logs in Render Dashboard → Your Service → **Logs** tab

### Common Issues

**1. Database Connection Errors**
```
Fix: Check DATABASE_URL is set correctly
```

**2. Model Not Found**
```
Fix: Ensure models/ directory is in repository
```

**3. CORS Errors**
```
Fix: Update ALLOWED_ORIGINS to include your Render URL
```

**4. Static Files Not Loading**
```
Fix: Ensure ui/ directory is in repository
```

---

## 🔄 Continuous Deployment

Render automatically deploys when you push to your connected Git branch!

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will:
1. Pull latest code
2. Install dependencies
3. Restart service
4. Deploy automatically ✅

---

## 💰 Cost Optimization

### Free Tier Limits

- Web Service: Spins down after 15 min inactivity (takes ~30s to wake up)
- PostgreSQL: 90 days of inactivity before deletion
- 750 hours/month free compute

### Tips

- Use a single web service to serve both API and frontend
- Enable "Auto-Deploy" only for production branch
- Use PostgreSQL connection pooling

---

## 🔒 Security Checklist

✅ Change default JWT_SECRET
✅ Use strong admin password
✅ Set DATABASE_URL as secret
✅ Enable HTTPS (automatic on Render)
✅ Configure CORS properly
✅ Regularly update dependencies

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)

---

## 🆘 Support

If you encounter issues:

1. Check Render logs (Dashboard → Service → Logs)
2. Verify environment variables
3. Test locally with `FRONTEND_URL` set to your Render URL
4. Check GitHub repository is accessible

---

**🎉 Your H. pylori CDSS is now deployed and accessible worldwide!**

