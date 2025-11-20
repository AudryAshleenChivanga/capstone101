# Model Management Troubleshooting Guide

## Issue: Model Management Dashboard Not Working in Production

### Root Cause Analysis

The Model Management system is not fully operational in the Render free tier deployment due to **ephemeral storage** limitations.

**What's Happening**:
1. ✅ Code is correct and pushed to GitHub
2. ✅ Routes are registered (`routes_model_management.py`)
3. ✅ Database models are defined (`PredictionLog`, `ModelTraining`)
4. ✅ Auto-creation script runs on startup
5. ❌ **BUT**: Render free tier resets on every deploy, losing data

### Current Status

**What IS Working**:
- ✅ Frontend UI (`ui/model_management.html`) renders correctly
- ✅ Navigation from Admin Panel works
- ✅ API endpoints are registered and responding
- ✅ Database tables are created on startup

**What IS NOT Working**:
- ❌ No historical prediction data (requires persistent logging)
- ❌ Charts show "No data" (requires accumulated data over time)
- ❌ Model retraining requires persistent storage
- ❌ Version history not retained across deploys

---

## Solution Options

### Option 1: Migrate to PostgreSQL (Recommended for Production)

**Why PostgreSQL**:
- Render offers **free PostgreSQL** instances (persistent storage)
- Current system uses SQLite (file-based, not persistent on Render free tier)
- PostgreSQL allows 90-day retention on free tier

**Implementation Steps**:

1. **Create PostgreSQL Instance on Render**:
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Select "Free" plan
   - Name: `h-pylori-cdss-db`
   - Copy the "Internal Database URL"

2. **Update Environment Variables**:
   - In your Render Web Service, go to "Environment"
   - Add new variable:
     ```
     DATABASE_URL=postgresql://[paste Internal Database URL]
     ```
   - Remove or update `SQLALCHEMY_DATABASE_URL` if it exists

3. **Update `app/config.py`**:
   ```python
   # Existing code
   from pydantic_settings import BaseSettings
   import os
   
   class Settings(BaseSettings):
       # ... existing settings ...
       
       # Database URL (use PostgreSQL in production, SQLite in development)
       SQLALCHEMY_DATABASE_URL: str = os.getenv(
           "DATABASE_URL",
           "sqlite:///./hp_cdss.db"  # Fallback for local development
       )
   ```

4. **Redeploy**:
   - Render will automatically redeploy
   - Database tables will be created in PostgreSQL
   - Data will persist across deploys

**Cost**: FREE (Render provides 90-day retention, 1GB storage)

---

### Option 2: Demo with Local/Screenshots (For Presentation)

**For Your Video Presentation**:

If you cannot set up PostgreSQL before your submission, you can:

1. **Run System Locally**:
   ```bash
   # Terminal
   python -m uvicorn main:app --reload
   ```

2. **Generate Mock Data** (Quick Script):
   Create `generate_mock_predictions.py`:
   ```python
   from app.db import SessionLocal
   from app.models import PredictionLog, ModelTraining
   from datetime import datetime, timedelta
   import random
   
   db = SessionLocal()
   
   # Create 100 mock predictions over last 30 days
   for i in range(100):
       days_ago = random.randint(0, 30)
       created_at = datetime.utcnow() - timedelta(days=days_ago)
       
       prediction_log = PredictionLog(
           model_name="screening",
           model_version="v1.0.0",
           user_id=1,  # Admin user
           case_id=i + 1,
           input_features={"age": random.randint(20, 70), "symptom_count": random.randint(0, 5)},
           prediction="positive" if random.random() > 0.4 else "negative",
           prediction_proba=random.uniform(0.5, 0.95),
           created_at=created_at
       )
       db.add(prediction_log)
   
   db.commit()
   print("[OK] 100 mock predictions created!")
   db.close()
   ```

   Run it:
   ```bash
   python generate_mock_predictions.py
   ```

3. **Record Video Locally**:
   - Navigate to `http://localhost:8000/ui/model_management.html`
   - Charts will populate with mock data
   - Record this for your video presentation

4. **Acknowledge in Video**:
   "This Model Management dashboard is shown in a local development environment with simulated data. The full production deployment requires PostgreSQL integration, which is documented in my repository as future work."

---

### Option 3: Show Concept with Partial Functionality

**Highlight What's Built**:

Even if the dashboard shows "No data", you can still demonstrate in your video:

1. **UI Design**:
   "I've built a comprehensive Model Management interface with three key sections..."

2. **Code Architecture**:
   "Let me show you the backend logic..." (show `routes_model_management.py` in editor)

3. **Database Schema**:
   "I've designed two core tables: `PredictionLog` and `ModelTraining`..." (show `app/models.py`)

4. **Future Deployment Plan**:
   "Full deployment requires PostgreSQL migration, estimated 2 hours implementation time..."

**Strengths of This Approach**:
- Shows your system design skills
- Demonstrates understanding of production challenges
- Highlights your honesty and transparency
- Evaluators appreciate realistic problem-solving

---

## Quick Fix: Show Static Example

**If you have <1 hour before recording**:

1. **Take Screenshot of UI**:
   Save `ui/model_management.html` opened in browser (even with "No data")

2. **Create Mockup with Data**:
   - Use browser DevTools to edit HTML
   - Manually insert fake chart data
   - Take screenshot
   - Show in video: "This mockup demonstrates the intended functionality..."

3. **Explain in Video**:
   "Due to Render free tier limitations, I'm showing a mockup of the intended Model Management dashboard. The full implementation is code-complete and documented in my repository."

---

## For Your Video Presentation

### Script Segment:

**"Let me show you the Model Management system I've built..."**

**[Navigate to Admin Panel → Click "AI Model Management"]**

**[If working locally with mock data]**:
"This dashboard provides administrators with real-time model health monitoring. You can see prediction trends over the last 30 days, model performance metrics, and recent predictions. The system supports model retraining and version control, ensuring ongoing accuracy as disease patterns evolve."

**[If not working in production]**:
"I've designed and implemented a Model Management system with health monitoring, retraining capabilities, and version control. While the full deployment requires PostgreSQL integration - a limitation of the free hosting tier I'm using - the architecture is complete and documented. Let me show you the code structure..."

**[Switch to VSCode or GitHub, show files]**:
- `routes_model_management.py` - API endpoints
- `app/models.py` - `PredictionLog` and `ModelTraining` tables
- `ui/model_management.html` - Dashboard UI
- `app/ml_retraining.py` - Retraining logic

**[Back to camera]**:
"This represents a critical ethical commitment to ongoing model maintenance. AI models can degrade over time, so having infrastructure for monitoring and retraining ensures the system continues to benefit patients safely. This is part of the principle of **ongoing beneficence** - our ethical responsibility doesn't end at deployment."

---

## Recommended Action for Submission

**If you have 2-3 hours**:
→ **Option 1**: Set up PostgreSQL (best for real functionality)

**If you have 30 minutes**:
→ **Option 2**: Run locally with mock data, record video

**If you have <30 minutes**:
→ **Option 3**: Show concept with honest explanation

**All three options are acceptable!** Your evaluators understand real-world constraints. What matters is:
- ✅ You built the system (you did!)
- ✅ You understand the architecture (you do!)
- ✅ You can explain ethical implications (you can!)
- ✅ You're honest about limitations (you will be!)

---

## Contact

If you need help with any of these options before recording, let me know!

**Good luck with your presentation!** 🚀

