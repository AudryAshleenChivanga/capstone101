# Docker Deployment Guide for H. pylori CDSS

## 🐳 Local Development with Docker

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start

1. **Build and run the container:**
```bash
docker-compose up --build
```

2. **Access the application:**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

3. **Stop the container:**
```bash
docker-compose down
```

### Development Tips

**View logs:**
```bash
docker-compose logs -f web
```

**Restart after code changes:**
```bash
docker-compose restart web
```

**Rebuild after dependency changes:**
```bash
docker-compose up --build
```

**Shell into container:**
```bash
docker-compose exec web bash
```

---

## 🚀 Deploying to Render with Docker

### Method 1: Using Render Dashboard (Easiest)

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `AudryAshleenChivanga/capstone101`
   - Select branch: `main`

3. **Configure Service:**
   - **Name:** `h-pylori-cdss`
   - **Region:** Oregon (or closest to you)
   - **Branch:** `main`
   - **Environment:** `Docker` ⚠️ **IMPORTANT!**
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Command:** (leave empty, uses CMD from Dockerfile)

4. **Set Environment Variables:**
   Click "Environment" tab and add:
   
   ```
   JWT_SECRET=<click "Generate" button>
   JWT_EXPIRE_HOURS=24
   SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
   STAGE_MODEL_PATH=models/staging_3class.joblib
   SCREEN_THRESH=0.60
   ALLOWED_ORIGINS=https://your-app.onrender.com
   ```
   
   Optional (for SMS/Email features):
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+1234567890
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Your app will be live at: `https://your-app.onrender.com`

---

### Method 2: Using render.yaml (Infrastructure as Code)

1. **The `render.yaml` file is already in your repo**

2. **Go to Render Dashboard:**
   - Click "New +" → "Blueprint"
   - Connect repository: `AudryAshleenChivanga/capstone101`
   - Render will detect `render.yaml` automatically

3. **Review and Deploy:**
   - Review the configuration
   - Click "Apply"
   - Render will create all services defined in the YAML

4. **Set Secrets:**
   After deployment, add sensitive environment variables:
   - Go to service → Environment
   - Add: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, etc.

---

## 🔧 Troubleshooting

### Build Fails

**Error: "Can't find requirements.txt"**
- Ensure `requirements.txt` is in root directory
- Check `.dockerignore` isn't excluding it

**Error: "No space left on device"**
- Render free tier has limited build space
- Remove unnecessary files via `.dockerignore`

### Runtime Issues

**Error: "Application failed to respond"**
- Check logs in Render dashboard
- Verify `PORT` environment variable is being used
- Ensure health check endpoint `/health` works

**Error: "Module not found"**
- Rebuild the Docker image: Manual Deploy → Clear cache → Deploy
- Check all files are copied in Dockerfile

**Error: "Database errors"**
- If using SQLite: It's read-only on Render (use PostgreSQL)
- If using PostgreSQL: Check `DATABASE_URL` format

### Static Files Not Loading

**CSS/JS not loading:**
- Check browser console for errors
- Verify `/ui` path in HTML files
- Ensure `ui/` directory is in Docker image

**Images not showing:**
- Check `/images` path
- Verify `images/` directory is copied
- Check file extensions match HTML references

---

## 📊 Monitoring Your Dockerized App

### Check Health
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "H. pylori CDSS",
  "version": "1.0.0"
}
```

### View Logs on Render
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Watch real-time logs

### Monitor Performance
- Render Dashboard → Metrics
- View: CPU usage, Memory, Response times
- Set up alerts if needed

---

## 🎯 Production Optimizations

### For Better Performance:

1. **Upgrade Render Plan:**
   - Free: 512MB RAM, sleeps after inactivity
   - Starter ($7/mo): 1GB RAM, always on
   - Standard ($25/mo): 2GB RAM, better performance

2. **Use PostgreSQL Database:**
   - Uncomment database section in `render.yaml`
   - Free tier: 90 days, then $7/mo
   - Better than SQLite for production

3. **Enable Health Checks:**
   - Already configured in Dockerfile
   - Render auto-restarts if health check fails

4. **Set Up CDN (Optional):**
   - Use Cloudflare for static assets
   - Faster loading worldwide

---

## 🔐 Security Checklist

- ✅ JWT_SECRET is randomly generated (not default)
- ✅ Database credentials are environment variables
- ✅ CORS restricted to your domain
- ✅ HTTPS enabled by default on Render
- ✅ Security headers configured in middleware
- ✅ Secrets not committed to Git

---

## 📝 Quick Commands Reference

```bash
# Local Development
docker-compose up --build              # Build and start
docker-compose down                    # Stop
docker-compose logs -f web             # View logs
docker-compose exec web bash           # Shell access

# Docker Build (standalone)
docker build -t hpylori-cdss .         # Build image
docker run -p 8000:8000 hpylori-cdss   # Run container

# Deploy to Render
git add -A
git commit -m "Deploy with Docker"
git push origin main                   # Auto-deploys if connected
```

---

## 🆘 Need Help?

1. **Check Render Logs** - Most issues show here
2. **Test Locally First** - Use `docker-compose up`
3. **Verify Environment Variables** - Common source of errors
4. **Health Check** - Visit `/health` endpoint
5. **API Docs** - Visit `/docs` to test endpoints

---

## ✅ Deployment Checklist

Before deploying:
- [ ] All code committed to Git
- [ ] `requirements.txt` up to date
- [ ] Environment variables configured on Render
- [ ] ML model files (`.joblib`) in repository
- [ ] UI files in `ui/` directory
- [ ] Images in `images/` directory
- [ ] Health check endpoint working
- [ ] Tested locally with Docker

After deploying:
- [ ] Health check returns 200 OK
- [ ] Landing page loads
- [ ] Login works
- [ ] Dashboard accessible
- [ ] API endpoints respond
- [ ] ML predictions work
- [ ] Images load correctly

---

**Your app is now Dockerized and ready for production! 🎉**

