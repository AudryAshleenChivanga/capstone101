# AI Model Management System - User Guide

## Overview

The Model Management System allows administrators to:
- **Monitor model health** in real-time (accuracy, predictions, performance)
- **Retrain models** using data collected over time (e.g., last 30 days)
- **Manage model versions** and deploy new versions to production
- **Track all predictions** for continuous improvement
- **View performance metrics** and data drift indicators

---

## Features

### 1. Model Health Dashboard
- View current model version and status
- See total predictions and recent activity (last 30 days)
- Monitor accuracy, precision, recall, F1 score, and AUC-ROC
- Check last training date

### 2. Automatic Prediction Logging
- Every prediction is automatically logged to the database
- Tracks input features, predictions, and timestamps
- Enables retraining with real-world data
- Supports outcome verification for accuracy tracking

### 3. Model Retraining
- Retrain models using data from the last 7, 14, 30, 60, or 90 days
- Automatic version numbering (v1.0.0, v1.0.1, etc.)
- Background training (doesn't block the application)
- Performance evaluation before deployment

### 4. Version Control
- Keep track of all model versions
- Compare performance across versions
- Deploy or rollback to any version
- Maintain model history

---

## Accessing the Model Management System

### Step 1: Login as Admin
1. Go to your application URL
2. Login with admin credentials (admin / Admin@2024)
3. Navigate to the Admin Panel

### Step 2: Access Model Management
1. In the Admin Panel, click the "🤖 AI Model Management" button
2. You'll see the Model Management Dashboard

---

## Using the Model Management Dashboard

### Monitoring Models

The dashboard shows cards for each model (Screening and Staging):

**Key Metrics:**
- **Accuracy**: Overall correctness of predictions
- **F1 Score**: Balance between precision and recall
- **Total Predictions**: All-time prediction count
- **Last 30 Days**: Recent prediction activity
- **Last Training**: When the model was last trained

**Status Indicators:**
- 🟢 **Active**: Currently deployed and serving predictions
- 🟡 **Training**: Model is being retrained
- 🔴 **Failed**: Training encountered an error

### Retraining a Model

**When to Retrain:**
- Accuracy has decreased
- You have at least 50 new verified predictions
- Data distribution has changed
- Regular maintenance (e.g., monthly)

**How to Retrain:**

1. Click the **"Retrain Model"** button on the model card
2. In the modal, select:
   - **Training Data Period**: How far back to collect data (e.g., last 30 days)
   - **Minimum Samples**: Safety threshold (default: 50)
   - **Notes**: Optional reason for retraining
3. Click **"Start Retraining"**

**What Happens:**
1. System collects predictions from the selected time period
2. Training runs in the background (takes 1-5 minutes)
3. New model version is created (e.g., v1.0.1)
4. Performance metrics are calculated
5. Model is saved but NOT deployed automatically

### Deploying a New Model Version

After retraining completes:

1. Go to **Model Versions** (coming soon in the UI)
2. Or use the API endpoint directly:
   ```bash
   POST /api/model-management/deploy/{training_id}
   ```
3. Review the new model's performance metrics
4. Deploy if performance is satisfactory
5. The old model is automatically archived

---

## API Endpoints

### Get All Models Health
```http
GET /api/model-management/health
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "status": "success",
  "models": [
    {
      "model_name": "screening",
      "current_version": "v1.0.0",
      "status": "active",
      "total_predictions": 1250,
      "predictions_last_30d": 342,
      "accuracy": 0.701,
      "f1_score": 0.783
    }
  ]
}
```

### Get Specific Model Health
```http
GET /api/model-management/health/{model_name}
Authorization: Bearer {admin_token}
```

### Trigger Retraining
```http
POST /api/model-management/retrain
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "model_name": "screening",
  "days_back": 30,
  "min_samples": 50,
  "notes": "Monthly maintenance retraining"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retraining started for screening model",
  "training_id": 3,
  "new_version": "v1.0.1",
  "estimated_samples": 342
}
```

### Check Training Status
```http
GET /api/model-management/training/status/{training_id}
Authorization: Bearer {admin_token}
```

### Deploy Model Version
```http
POST /api/model-management/deploy/{training_id}
Authorization: Bearer {admin_token}
```

### Get Recent Predictions
```http
GET /api/model-management/predictions/recent?limit=100
Authorization: Bearer {admin_token}
```

### Get Prediction Statistics
```http
GET /api/model-management/predictions/stats?model_name=screening&days_back=30
Authorization: Bearer {admin_token}
```

---

## Database Schema

### PredictionLog Table
Stores every prediction made by the system:
- `model_name`: Which model made the prediction
- `model_version`: Version used
- `input_features`: JSON of all input features
- `prediction`: Predicted class/value
- `prediction_proba`: Confidence score
- `actual_outcome`: True outcome (when verified)
- `outcome_verified`: Whether outcome is confirmed
- `created_at`: Timestamp

### ModelTraining Table
Tracks all model training sessions:
- `model_name`: screening or staging
- `model_version`: v1.0.0, v1.0.1, etc.
- `status`: training, completed, failed, active
- `accuracy`, `precision`, `recall`, `f1_score`, `auc_roc`: Metrics
- `is_production`: Is this the deployed model?
- `deployed_at`: When it went live
- `model_path`: File location

---

## How Prediction Logging Works

### Automatic Logging
Every time a prediction is made through `/api/recommend`:
1. Input features are captured
2. Prediction result is saved
3. Timestamp is recorded
4. Linked to case and user

### Outcome Verification
To improve retraining accuracy:
1. Clinicians can verify predictions
2. Mark actual outcomes (e.g., patient tested positive)
3. Verified data is prioritized for retraining

### Data Collection Flow
```
User Request → ML Prediction → Log to Database → (Optional) Outcome Verification → Available for Retraining
```

---

## Best Practices

### 1. Regular Monitoring
- Check model health weekly
- Review prediction statistics monthly
- Watch for accuracy degradation

### 2. Retraining Schedule
- **Screening Model**: Retrain every 30-60 days
- **Staging Model**: Retrain every 60-90 days
- **Emergency**: Retrain immediately if accuracy drops > 10%

### 3. Data Requirements
- Minimum 50 samples for retraining
- Prioritize verified outcomes
- Use at least 30 days of data for stability

### 4. Version Management
- Keep at least 3 recent versions
- Test new versions before deployment
- Have a rollback plan

### 5. Production Deployment
- Always test locally first
- Deploy during low-traffic periods
- Monitor performance after deployment
- Keep old version accessible for 24 hours

---

## Troubleshooting

### "Insufficient data for retraining"
**Problem**: Not enough predictions in the selected time period  
**Solution**: 
- Extend the time period (e.g., 60 or 90 days)
- Wait for more predictions to accumulate
- Lower `min_samples` (carefully)

### "Training failed"
**Problem**: Error during model training  
**Solution**:
- Check logs for specific error
- Verify data quality
- Ensure all required features are present
- Contact system administrator

### "Model not showing in dashboard"
**Problem**: Model health endpoint returns error  
**Solution**:
- Ensure you're logged in as admin
- Check database connection
- Verify ModelTraining records exist
- Run `create_model_tables.py` again

### Predictions not being logged
**Problem**: PredictionLog table is empty  
**Solution**:
- Verify table was created (`create_model_tables.py`)
- Check for errors in prediction endpoints
- Ensure logging function isn't failing silently

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] Run `create_model_tables.py` on production database
- [ ] Verify initial model records are created
- [ ] Test retraining locally
- [ ] Backup current models

### Deployment
- [ ] Push code to GitHub
- [ ] Update production environment variables (if needed)
- [ ] Restart Render service
- [ ] Verify database migrations ran successfully

### Post-Deployment
- [ ] Test model health endpoints
- [ ] Make a test prediction (verify logging)
- [ ] Access model management UI
- [ ] Check for errors in logs

### Monitoring
- [ ] Monitor prediction logs daily for first week
- [ ] Check model health dashboard weekly
- [ ] Plan first retraining cycle (30-60 days)

---

## Security Considerations

- **Admin Only**: Model management is restricted to admin role
- **Authentication**: All endpoints require JWT token
- **Audit Trail**: All retraining actions are logged with user ID
- **Model Versioning**: Old models are preserved, not deleted
- **Database Backup**: Regularly backup ModelTraining and PredictionLog tables

---

## Future Enhancements

Planned features:
1. **A/B Testing**: Deploy multiple models simultaneously
2. **Explainable AI**: Show why models made specific predictions
3. **Automated Retraining**: Schedule automatic retraining
4. **Performance Alerts**: Email notifications for accuracy drops
5. **Data Drift Detection**: Automatic detection of distribution changes
6. **Model Comparison**: Side-by-side version comparison
7. **Rollback Button**: One-click rollback to previous version

---

## Support

For issues or questions:
- Check application logs
- Review this guide
- Contact system administrator
- File an issue on GitHub

---

## Technical Architecture

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         v
┌─────────────────────────────┐
│  FastAPI Endpoint           │
│  /api/recommend             │
└────────┬────────────────────┘
         │
         v
┌─────────────────────────────┐
│  ML Model Prediction        │
│  (Screening/Staging)        │
└────────┬────────────────────┘
         │
         ├─────────────────────┐
         │                     │
         v                     v
┌──────────────────┐   ┌──────────────────┐
│ Return Result    │   │ Log Prediction   │
│ to User          │   │ to Database      │
└──────────────────┘   └────────┬─────────┘
                                │
                                v
                       ┌──────────────────┐
                       │ PredictionLog    │
                       │ Table            │
                       └────────┬─────────┘
                                │
                                v
                       ┌──────────────────┐
                       │ Used for         │
                       │ Retraining       │
                       └──────────────────┘
```

---

**Last Updated**: November 2024  
**Version**: 1.0.0  
**Author**: Audry Ashleen Chivanga

