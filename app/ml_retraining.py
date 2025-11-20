"""Machine Learning Model Retraining Logic."""
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.models import PredictionLog, ModelTraining, Case
from app.db import SessionLocal


# ============================================================================
# SCREENING MODEL RETRAINING
# ============================================================================

def retrain_screening_model(training_id: int, days_back: int, db: Session = None):
    """Retrain the screening model with recent prediction data."""
    if db is None:
        db = SessionLocal()
    
    try:
        training = db.query(ModelTraining).filter(ModelTraining.id == training_id).first()
        if not training:
            print(f"Training record {training_id} not found")
            return
        
        print(f"Starting retraining for screening model v{training.model_version}")
        
        # Get recent predictions with outcomes
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        predictions = db.query(PredictionLog).filter(
            PredictionLog.model_name == "screening",
            PredictionLog.created_at >= cutoff_date,
            PredictionLog.outcome_verified == 1  # Only verified outcomes
        ).all()
        
        if len(predictions) < 50:
            # Not enough data - load original training data
            print("Insufficient new data. Loading original training data...")
            df = _load_original_screening_data()
        else:
            # Convert predictions to DataFrame
            df = _predictions_to_dataframe(predictions, "screening")
        
        print(f"Training data size: {len(df)} samples")
        
        # Prepare features
        feature_cols = [
            'age', 'sex', 'residence', 'sanitation', 'water_source', 'crowding',
            'poverty_index', 'smoking', 'nsaid_use', 'prior_antibiotics_3m',
            'epigastric_pain', 'nausea', 'bloating', 'early_satiety', 'weight_loss',
            'hemoglobin', 'CRP', 'wbc_count', 'platelet_count', 'albumin'
        ]
        
        # Handle missing columns
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        X = df[feature_cols]
        y = df['hp_pos'].apply(lambda x: 1 if x == "positive" or x == 1 else 0)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        print("Training Random Forest model...")
        rf = RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=2,
            class_weight='balanced_subsample',
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train_scaled, y_train)
        
        # Calibrate probabilities
        print("Calibrating probabilities...")
        calibrated_model = CalibratedClassifierCV(rf, method='sigmoid', cv=3)
        calibrated_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = calibrated_model.predict(X_test_scaled)
        y_proba = calibrated_model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc_roc = roc_auc_score(y_test, y_proba)
        
        print(f"Model Performance:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  AUC-ROC:   {auc_roc:.4f}")
        
        # Save model
        model_dir = "models/versions"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"screening_{training.model_version}.joblib")
        
        # Package model with scaler and feature names
        model_package = {
            'model': calibrated_model,
            'scaler': scaler,
            'feature_names': feature_cols,
            'version': training.model_version,
            'trained_at': datetime.utcnow()
        }
        joblib.dump(model_package, model_path)
        print(f"Model saved to {model_path}")
        
        # Update training record
        training.status = "completed"
        training.training_end = datetime.utcnow()
        training.dataset_size = len(df)
        training.training_samples = len(X_train)
        training.validation_samples = len(X_test)
        training.accuracy = float(accuracy)
        training.precision = float(precision)
        training.recall = float(recall)
        training.f1_score = float(f1)
        training.auc_roc = float(auc_roc)
        training.model_path = model_path
        training.config_data = {
            'n_estimators': 400,
            'features': feature_cols,
            'calibration': 'sigmoid',
            'data_period_days': days_back
        }
        db.commit()
        
        print(f"✓ Retraining completed successfully for screening model v{training.model_version}")
        
    except Exception as e:
        print(f"Error during retraining: {str(e)}")
        if training:
            training.status = "failed"
            training.notes = f"Error: {str(e)}"
            db.commit()
        raise
    finally:
        if db:
            db.close()


# ============================================================================
# STAGING MODEL RETRAINING
# ============================================================================

def retrain_staging_model(training_id: int, days_back: int, db: Session = None):
    """Retrain the staging model with recent prediction data."""
    if db is None:
        db = SessionLocal()
    
    try:
        training = db.query(ModelTraining).filter(ModelTraining.id == training_id).first()
        if not training:
            print(f"Training record {training_id} not found")
            return
        
        print(f"Starting retraining for staging model v{training.model_version}")
        
        # Get recent predictions with outcomes
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        predictions = db.query(PredictionLog).filter(
            PredictionLog.model_name == "staging",
            PredictionLog.created_at >= cutoff_date,
            PredictionLog.outcome_verified == 1
        ).all()
        
        if len(predictions) < 30:
            print("Insufficient new data. Loading original training data...")
            df = _load_original_staging_data()
        else:
            df = _predictions_to_dataframe(predictions, "staging")
        
        print(f"Training data size: {len(df)} samples")
        
        # Prepare features
        feature_cols = ['age', 'sex', 'mic_clari', 'mut_A2143G', 'mut_A2144G', 'double_mut']
        
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        X = df[feature_cols]
        y = df['stage_proxy_3c']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        
        # Train Random Forest
        print("Training Random Forest model...")
        rf = RandomForestClassifier(
            n_estimators=400,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        print(f"Model Performance:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        
        # Save model
        model_dir = "models/versions"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"staging_{training.model_version}.joblib")
        
        model_package = {
            'model': rf,
            'feature_names': feature_cols,
            'version': training.model_version,
            'trained_at': datetime.utcnow()
        }
        joblib.dump(model_package, model_path)
        print(f"Model saved to {model_path}")
        
        # Update training record
        training.status = "completed"
        training.training_end = datetime.utcnow()
        training.dataset_size = len(df)
        training.training_samples = len(X_train)
        training.validation_samples = len(X_test)
        training.accuracy = float(accuracy)
        training.precision = float(precision)
        training.recall = float(recall)
        training.f1_score = float(f1)
        training.model_path = model_path
        training.config_data = {
            'n_estimators': 400,
            'features': feature_cols,
            'data_period_days': days_back
        }
        db.commit()
        
        print(f"✓ Retraining completed successfully for staging model v{training.model_version}")
        
    except Exception as e:
        print(f"Error during retraining: {str(e)}")
        if training:
            training.status = "failed"
            training.notes = f"Error: {str(e)}"
            db.commit()
        raise
    finally:
        if db:
            db.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _predictions_to_dataframe(predictions: list, model_name: str) -> pd.DataFrame:
    """Convert prediction logs to training DataFrame."""
    data = []
    for p in predictions:
        features = p.input_features.copy()
        
        if model_name == "screening":
            features['hp_pos'] = p.actual_outcome
        elif model_name == "staging":
            features['stage_proxy_3c'] = p.actual_outcome
        
        data.append(features)
    
    return pd.DataFrame(data)


def _load_original_screening_data() -> pd.DataFrame:
    """Load original screening training data as fallback."""
    # Try to load from data directory
    data_path = "data/df_screen.csv"
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    
    # Fallback: generate synthetic data
    print("Warning: Using synthetic data for training")
    np.random.seed(42)
    n_samples = 1000
    
    df = pd.DataFrame({
        'age': np.random.randint(18, 80, n_samples),
        'sex': np.random.choice([0, 1], n_samples),
        'residence': np.random.choice([0, 1], n_samples),
        'sanitation': np.random.choice([0, 1], n_samples),
        'water_source': np.random.choice([0, 1, 2], n_samples),
        'crowding': np.random.choice([0, 1], n_samples),
        'poverty_index': np.random.uniform(0, 1, n_samples),
        'smoking': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'nsaid_use': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'prior_antibiotics_3m': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'epigastric_pain': np.random.choice([0, 1], n_samples, p=[0.5, 0.5]),
        'nausea': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'bloating': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'early_satiety': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'weight_loss': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'hemoglobin': np.random.uniform(10, 16, n_samples),
        'CRP': np.random.uniform(0, 50, n_samples),
        'wbc_count': np.random.uniform(4, 12, n_samples),
        'platelet_count': np.random.uniform(150, 400, n_samples),
        'albumin': np.random.uniform(3.5, 5.0, n_samples),
        'hp_pos': np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    })
    
    return df


def _load_original_staging_data() -> pd.DataFrame:
    """Load original staging training data as fallback."""
    data_path = "data/df_stage.csv"
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    
    # Fallback: generate synthetic data
    print("Warning: Using synthetic data for training")
    np.random.seed(42)
    n_samples = 100
    
    df = pd.DataFrame({
        'age': np.random.randint(25, 75, n_samples),
        'sex': np.random.choice([0, 1], n_samples),
        'mic_clari': np.random.choice([0.5, 1, 2, 4, 8, 16, 32, 64, 128], n_samples),
        'mut_A2143G': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'mut_A2144G': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'double_mut': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'stage_proxy_3c': np.random.choice(['low', 'moderate', 'high'], n_samples, p=[0.2, 0.6, 0.2])
    })
    
    return df

