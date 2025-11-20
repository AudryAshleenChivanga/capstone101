# Setting Up Model Management System in Production

## Quick Setup Guide for Render Deployment

### Step 1: Access Render Shell

1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your `h-pylori-cdss` service
3. Click on **"Shell"** tab
4. Run the following commands:

```bash
# Navigate to your project directory
cd /opt/render/project/src

# Create model management tables
python create_model_tables.py
```

**Expected Output:**
```
[OK] Tables created successfully
Found 0 existing model training records
Creating initial model training records...
[OK] Initial model records created
[OK] PredictionLog table exists with 0 records
```

### Step 2: Verify Deployment

1. Go to your deployed application: https://h-pylori-cdss.onrender.com/
2. Login as admin (admin / Admin@2024)
3. Click on **"Admin Panel"**
4. Click on **"🤖 AI Model Management"** button

### Step 3: Test the System

#### Test 1: View Model Health
- You should see two model cards (Screening and Staging)
- Check that metrics are displayed (accuracy, F1 score, etc.)
- Verify "Last Training" shows initial date

#### Test 2: Make a Prediction (to test logging)
1. Go back to Dashboard
2. Run a screening test with any patient data
3. Return to Model Management
4. Refresh the page
5. Check "Recent Predictions" table - you should see your prediction logged

#### Test 3: Attempt Retraining (will fail due to insufficient data, which is expected)
1. Click "Retrain Model" on the Screening card
2. Leave defaults (Last 30 days, 50 samples)
3. Click "Start Retraining"
4. **Expected**: Error message "Insufficient data for retraining"
5. This is correct! You need at least 50 predictions before retraining

### Step 4: Environment Variables (Optional)

If you need to adjust settings, add these environment variables in Render:

```env
# Model paths (already configured)
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib

# Model version directory
MODEL_VERSION_DIR=models/versions
```

---

## What Was Deployed

### New Files

1. **`app/routes_model_management.py`** - API endpoints for model management
   - Health monitoring
   - Retraining triggers
   - Version management
   - Prediction statistics

2. **`app/ml_retraining.py`** - Retraining logic
   - Screening model retraining
   - Staging model retraining
   - Data loading and preprocessing
   - Model evaluation

3. **`ui/model_management.html`** - Admin dashboard
   - Model health cards
   - Retraining interface
   - Recent predictions table
   - Real-time updates

4. **`create_model_tables.py`** - Database setup script
   - Creates PredictionLog table
   - Creates ModelTraining table
   - Initializes model records

### Modified Files

1. **`app/models.py`** - Added database models
   - `PredictionLog` - Stores all predictions
   - Enhanced `ModelTraining` - Already existed, now fully utilized

2. **`app/routes_reco.py`** - Prediction logging
   - Logs every screening prediction
   - Logs every staging prediction
   - Tracks input features and outcomes

3. **`main.py`** - Router registration
   - Added model management router

4. **`ui/admin.html`** - Navigation
   - Added "AI Model Management" button

---

## How to Use in Production

### For Admins

#### Daily/Weekly Monitoring
1. Check model health dashboard weekly
2. Monitor prediction counts
3. Watch for accuracy changes

#### Monthly Retraining (After Sufficient Data)
Once you have 50+ predictions:
1. Go to Model Management
2. Click "Retrain Model"
3. Select "Last 30 days"
4. Add notes (e.g., "Monthly maintenance")
5. Click "Start Retraining"
6. Wait 2-5 minutes for completion
7. Check training status
8. Deploy if metrics are satisfactory

### For API Users

#### Get Model Health
```bash
curl https://h-pylori-cdss.onrender.com/api/model-management/health \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Trigger Retraining
```bash
curl -X POST https://h-pylori-cdss.onrender.com/api/model-management/retrain \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "screening",
    "days_back": 30,
    "min_samples": 50,
    "notes": "Monthly retraining"
  }'
```

#### Get Recent Predictions
```bash
curl https://h-pylori-cdss.onrender.com/api/model-management/predictions/recent?limit=20 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Verification Checklist

After deployment, verify:

- [ ] Database tables created successfully
- [ ] Initial model records exist (2 models)
- [ ] Model Management UI is accessible
- [ ] Model health dashboard loads correctly
- [ ] Prediction logging works (make a test prediction)
- [ ] Recent predictions table shows data
- [ ] Retraining modal opens correctly
- [ ] API endpoints respond with 200 (except retraining without data)

---

## Troubleshooting Production Issues

### Issue: "Model not found" error
**Solution**: Run `create_model_tables.py` in Render shell

### Issue: Database doesn't persist after restart
**Render Note**: On Render's free tier, you're using SQLite which is ephemeral. For production, consider:
1. Upgrading to PostgreSQL on Render
2. Or accepting that model management data resets on redeploy
3. Initial models will be recreated automatically on startup

### Issue: Retraining always fails
**Common Causes**:
1. Not enough data (need 50+ predictions)
2. Database connection issue
3. Model files not writable

**Check Logs**:
```bash
# In Render shell
cd /opt/render/project/src
python -m uvicorn main:app --log-level debug
```

### Issue: Can't access Model Management UI
**Solutions**:
1. Clear browser cache
2. Check you're logged in as admin
3. Verify route registration in main.py
4. Check Render logs for errors

---

## Performance Considerations

### Database Growth
- **PredictionLog**: ~1KB per prediction
- **ModelTraining**: ~5KB per training session
- **Estimated Growth**: ~1MB per 1000 predictions

### Retraining Time
- **Screening Model**: 2-4 minutes (400 trees)
- **Staging Model**: 30-60 seconds (smaller dataset)
- **Runs in Background**: Doesn't block other requests

### Production Database Recommendation
For long-term production use, switch to PostgreSQL:

1. In Render dashboard, create PostgreSQL database
2. Add `DATABASE_URL` environment variable
3. Update `app/db.py` to use PostgreSQL URL
4. Run migrations

---

## Next Steps

### Short Term (This Week)
1. Deploy to production ✅
2. Test model management UI ✅
3. Make 10-20 test predictions to verify logging
4. Verify data appears in Recent Predictions table

### Medium Term (Next Month)
1. Accumulate 50+ real predictions
2. Perform first retraining cycle
3. Compare old vs new model performance
4. Deploy new version if improved

### Long Term (3-6 Months)
1. Establish monthly retraining schedule
2. Track model performance trends
3. Implement outcome verification workflow
4. Consider automated retraining

---

## Support & Documentation

- **Full User Guide**: See `MODEL_MANAGEMENT_GUIDE.md`
- **API Documentation**: https://h-pylori-cdss.onrender.com/docs
- **Technical Support**: Open GitHub issue
- **Emergency**: Contact system administrator

---

**Status**: ✅ READY FOR PRODUCTION  
**Deployed**: November 2024  
**Version**: 1.0.0

