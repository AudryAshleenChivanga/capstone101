"""Create new model management database tables."""
from app.db import create_tables, SessionLocal
from app.models import ModelTraining
from datetime import datetime

print("Creating/updating database tables...")
create_tables()
print("[OK] Tables created successfully")

# Check if tables exist
db = SessionLocal()

# Check if we have any model training records
existing_records = db.query(ModelTraining).count()
print(f"\nFound {existing_records} existing model training records")

if existing_records == 0:
    print("\nCreating initial model training records for current production models...")
    
    # Create record for screening model
    screening_model = ModelTraining(
        model_name="screening",
        model_version="v1.0.0",
        model_type="classification",
        training_start=datetime(2024, 10, 1),
        training_end=datetime(2024, 10, 1),
        status="active",
        dataset_size=25000,
        training_samples=18750,
        validation_samples=6250,
        accuracy=0.701,
        precision=0.727,
        recall=0.849,
        f1_score=0.783,
        auc_roc=0.738,
        model_path="models/screening_hp_pos_calibrated.joblib",
        config_data={
            "n_estimators": 400,
            "calibration": "sigmoid",
            "features": 20
        },
        is_production=1,
        deployed_at=datetime(2024, 10, 1),
        notes="Initial production model"
    )
    db.add(screening_model)
    
    # Create record for staging model
    staging_model = ModelTraining(
        model_name="staging",
        model_version="v1.0.0",
        model_type="classification",
        training_start=datetime(2024, 10, 1),
        training_end=datetime(2024, 10, 1),
        status="active",
        dataset_size=38,
        training_samples=28,
        validation_samples=10,
        accuracy=0.90,
        precision=0.875,
        recall=1.0,
        f1_score=0.933,
        model_path="models/staging_3class.joblib",
        config_data={
            "n_estimators": 400,
            "class_weight": "balanced",
            "features": 6
        },
        is_production=1,
        deployed_at=datetime(2024, 10, 1),
        notes="Initial production model"
    )
    db.add(staging_model)
    
    db.commit()
    print("[OK] Initial model records created")
else:
    print("[OK] Model records already exist")

# Verify PredictionLog table exists
from app.models import PredictionLog
prediction_count = db.query(PredictionLog).count()
print(f"\n[OK] PredictionLog table exists with {prediction_count} records")

db.close()

print("\n" + "="*60)
print("Database setup complete!")
print("="*60)
print("\nYou can now:")
print("1. Start the application: python -m uvicorn main:app --reload")
print("2. Access Model Management: http://localhost:8000/ui/model_management.html")
print("3. Login as admin (admin / Admin@2024)")
print("\nNote: Predictions will be automatically logged starting now.")

