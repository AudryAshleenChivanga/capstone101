"""Model Management Routes - Health Monitoring and Retraining."""
import os
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from pydantic import BaseModel

from app.db import get_db
from app.auth import get_current_user, require_role
from app.models import User, ModelTraining, PredictionLog, Case
from app.ml_retraining import retrain_screening_model, retrain_staging_model

router = APIRouter(prefix="/api/model-management", tags=["model_management"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ModelHealthResponse(BaseModel):
    model_name: str
    current_version: str
    status: str
    deployed_at: Optional[datetime]
    total_predictions: int
    predictions_last_30d: int
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    auc_roc: Optional[float]
    last_training: Optional[datetime]


class RetrainingRequest(BaseModel):
    model_name: str  # "screening" or "staging"
    days_back: int = 30
    min_samples: int = 50
    notes: Optional[str] = None


class ModelVersionInfo(BaseModel):
    id: int
    model_name: str
    version: str
    accuracy: Optional[float]
    f1_score: Optional[float]
    is_production: bool
    deployed_at: Optional[datetime]
    created_at: datetime


# ============================================================================
# MODEL HEALTH & STATUS
# ============================================================================

@router.get("/health", dependencies=[Depends(require_role(["admin"]))])
async def get_all_models_health(db: Session = Depends(get_db)):
    """Get health status for all models (admin only)."""
    models_info = []
    
    for model_name in ["screening", "staging"]:
        health = await get_model_health(model_name, db)
        models_info.append(health)
    
    return {
        "status": "success",
        "models": models_info,
        "timestamp": datetime.utcnow()
    }


@router.get("/health/{model_name}", dependencies=[Depends(require_role(["admin"]))])
async def get_model_health(model_name: str, db: Session = Depends(get_db)):
    """Get detailed health status for a specific model."""
    
    # Get production model info
    prod_model = db.query(ModelTraining).filter(
        ModelTraining.model_name == model_name,
        ModelTraining.is_production == 1
    ).first()
    
    if not prod_model:
        raise HTTPException(status_code=404, detail=f"No production model found for {model_name}")
    
    # Get prediction counts
    total_predictions = db.query(func.count(PredictionLog.id)).filter(
        PredictionLog.model_name == model_name
    ).scalar() or 0
    
    # Last 30 days predictions
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    predictions_30d = db.query(func.count(PredictionLog.id)).filter(
        PredictionLog.model_name == model_name,
        PredictionLog.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Calculate real-world accuracy (verified outcomes)
    verified_predictions = db.query(PredictionLog).filter(
        PredictionLog.model_name == model_name,
        PredictionLog.outcome_verified == 1,
        PredictionLog.created_at >= thirty_days_ago
    ).all()
    
    real_accuracy = None
    if verified_predictions:
        correct = sum(1 for p in verified_predictions if p.prediction == p.actual_outcome)
        real_accuracy = correct / len(verified_predictions)
    
    return ModelHealthResponse(
        model_name=model_name,
        current_version=prod_model.model_version,
        status=prod_model.status,
        deployed_at=prod_model.deployed_at,
        total_predictions=total_predictions,
        predictions_last_30d=predictions_30d,
        accuracy=real_accuracy if real_accuracy else prod_model.accuracy,
        precision=prod_model.precision,
        recall=prod_model.recall,
        f1_score=prod_model.f1_score,
        auc_roc=prod_model.auc_roc,
        last_training=prod_model.training_end
    )


@router.get("/predictions/recent", dependencies=[Depends(require_role(["admin"]))])
async def get_recent_predictions(
    model_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent predictions for monitoring."""
    query = db.query(PredictionLog)
    
    if model_name:
        query = query.filter(PredictionLog.model_name == model_name)
    
    predictions = query.order_by(desc(PredictionLog.created_at)).limit(limit).all()
    
    return {
        "status": "success",
        "count": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "model_name": p.model_name,
                "prediction": p.prediction,
                "prediction_proba": p.prediction_proba,
                "actual_outcome": p.actual_outcome,
                "outcome_verified": p.outcome_verified,
                "created_at": p.created_at,
                "case_id": p.case_id
            }
            for p in predictions
        ]
    }


@router.get("/predictions/stats", dependencies=[Depends(require_role(["admin"]))])
async def get_prediction_statistics(
    model_name: str,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """Get prediction statistics for data drift monitoring."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    predictions = db.query(PredictionLog).filter(
        PredictionLog.model_name == model_name,
        PredictionLog.created_at >= cutoff_date
    ).all()
    
    if not predictions:
        return {
            "status": "no_data",
            "message": f"No predictions found in last {days_back} days"
        }
    
    # Calculate statistics
    total = len(predictions)
    
    if model_name == "screening":
        positive_preds = sum(1 for p in predictions if p.prediction == "positive")
        avg_proba = sum(p.prediction_proba or 0 for p in predictions) / total
        
        stats = {
            "total_predictions": total,
            "positive_predictions": positive_preds,
            "negative_predictions": total - positive_preds,
            "positive_rate": positive_preds / total,
            "avg_probability": avg_proba
        }
    elif model_name == "staging":
        stage_counts = {}
        for p in predictions:
            stage = p.prediction
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        stats = {
            "total_predictions": total,
            "stage_distribution": stage_counts
        }
    else:
        stats = {"total_predictions": total}
    
    # Verified outcomes
    verified = [p for p in predictions if p.outcome_verified]
    if verified:
        correct = sum(1 for p in verified if p.prediction == p.actual_outcome)
        stats["verified_count"] = len(verified)
        stats["real_world_accuracy"] = correct / len(verified)
    
    return {
        "status": "success",
        "model_name": model_name,
        "period_days": days_back,
        "statistics": stats
    }


# ============================================================================
# MODEL VERSIONS
# ============================================================================

@router.get("/versions/{model_name}", dependencies=[Depends(require_role(["admin"]))])
async def get_model_versions(model_name: str, db: Session = Depends(get_db)):
    """Get all versions of a model."""
    versions = db.query(ModelTraining).filter(
        ModelTraining.model_name == model_name
    ).order_by(desc(ModelTraining.created_at)).all()
    
    return {
        "status": "success",
        "model_name": model_name,
        "versions": [
            ModelVersionInfo(
                id=v.id,
                model_name=v.model_name,
                version=v.model_version,
                accuracy=v.accuracy,
                f1_score=v.f1_score,
                is_production=bool(v.is_production),
                deployed_at=v.deployed_at,
                created_at=v.created_at
            )
            for v in versions
        ]
    }


# ============================================================================
# MODEL RETRAINING
# ============================================================================

@router.post("/retrain", dependencies=[Depends(require_role(["admin"]))])
async def trigger_model_retraining(
    request: RetrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger model retraining with recent data (admin only)."""
    
    # Validate model name
    if request.model_name not in ["screening", "staging"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid model name. Must be 'screening' or 'staging'"
        )
    
    # Check if we have enough new data
    cutoff_date = datetime.utcnow() - timedelta(days=request.days_back)
    prediction_count = db.query(func.count(PredictionLog.id)).filter(
        PredictionLog.model_name == request.model_name,
        PredictionLog.created_at >= cutoff_date
    ).scalar() or 0
    
    if prediction_count < request.min_samples:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for retraining. Found {prediction_count} samples, minimum {request.min_samples} required."
        )
    
    # Create training record
    new_version = _generate_version_number(request.model_name, db)
    
    training_record = ModelTraining(
        model_name=request.model_name,
        model_version=new_version,
        model_type="classification",
        training_start=datetime.utcnow(),
        status="training",
        trained_by=current_user.id,
        notes=request.notes
    )
    db.add(training_record)
    db.commit()
    db.refresh(training_record)
    
    # Trigger retraining in background
    if request.model_name == "screening":
        background_tasks.add_task(
            retrain_screening_model,
            training_record.id,
            request.days_back,
            db
        )
    elif request.model_name == "staging":
        background_tasks.add_task(
            retrain_staging_model,
            training_record.id,
            request.days_back,
            db
        )
    
    return {
        "status": "success",
        "message": f"Retraining started for {request.model_name} model",
        "training_id": training_record.id,
        "new_version": new_version,
        "data_period_days": request.days_back,
        "estimated_samples": prediction_count
    }


@router.post("/deploy/{training_id}", dependencies=[Depends(require_role(["admin"]))])
async def deploy_model_version(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deploy a trained model version to production."""
    
    # Get the training record
    training = db.query(ModelTraining).filter(ModelTraining.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    if training.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot deploy model with status '{training.status}'. Must be 'completed'."
        )
    
    # Deactivate current production model
    current_prod = db.query(ModelTraining).filter(
        ModelTraining.model_name == training.model_name,
        ModelTraining.is_production == 1
    ).first()
    
    if current_prod:
        current_prod.is_production = 0
        current_prod.replaced_at = datetime.utcnow()
    
    # Activate new model
    training.is_production = 1
    training.deployed_at = datetime.utcnow()
    training.status = "active"
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Model {training.model_name} v{training.model_version} deployed to production",
        "model_name": training.model_name,
        "version": training.model_version,
        "replaced_version": current_prod.model_version if current_prod else None
    }


@router.get("/training/status/{training_id}", dependencies=[Depends(require_role(["admin"]))])
async def get_training_status(training_id: int, db: Session = Depends(get_db)):
    """Check the status of a training job."""
    training = db.query(ModelTraining).filter(ModelTraining.id == training_id).first()
    
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    return {
        "status": "success",
        "training_id": training.id,
        "model_name": training.model_name,
        "version": training.model_version,
        "training_status": training.status,
        "started_at": training.training_start,
        "completed_at": training.training_end,
        "accuracy": training.accuracy,
        "f1_score": training.f1_score,
        "is_production": bool(training.is_production),
        "notes": training.notes
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_version_number(model_name: str, db: Session) -> str:
    """Generate next version number for a model."""
    latest = db.query(ModelTraining).filter(
        ModelTraining.model_name == model_name
    ).order_by(desc(ModelTraining.created_at)).first()
    
    if not latest:
        return "v1.0.0"
    
    # Parse version (e.g., "v1.2.3" -> [1, 2, 3])
    try:
        parts = latest.model_version.replace("v", "").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        patch += 1
        return f"v{major}.{minor}.{patch}"
    except:
        # Fallback to timestamp-based version
        return f"v1.0.{int(datetime.utcnow().timestamp())}"

