"""Recommendation and case management routes."""
import io
import pandas as pd
import time
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db import get_db
from app.models import User, Case, Patient, PredictionLog
from app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    CaseResponse
)
from app.auth import get_current_user
from app.ml import get_recommendation
from app.config import settings
from app.utils.patient_utils import get_or_create_patient
import sklearn
import sys

router = APIRouter(tags=["recommendations"])


# ============================================================================
# PREDICTION LOGGING HELPER
# ============================================================================

def log_prediction(
    db: Session,
    model_name: str,
    input_features: dict,
    prediction: any,
    prediction_proba: float = None,
    prediction_probas: dict = None,
    user_id: int = None,
    case_id: int = None,
    patient_db_id: int = None,
    prediction_time: float = None
):
    """Log a prediction to the database for monitoring and retraining."""
    try:
        # Get current model version (if available)
        from app.models import ModelTraining
        current_model = db.query(ModelTraining).filter(
            ModelTraining.model_name == model_name,
            ModelTraining.is_production == 1
        ).first()
        
        model_version = current_model.model_version if current_model else "unknown"
        
        # Create prediction log
        pred_log = PredictionLog(
            model_name=model_name,
            model_version=model_version,
            input_features=input_features,
            prediction=str(prediction) if prediction is not None else None,
            prediction_proba=prediction_proba,
            prediction_probas=prediction_probas,
            user_id=user_id,
            case_id=case_id,
            patient_db_id=patient_db_id,
            prediction_time=prediction_time
        )
        
        db.add(pred_log)
        db.commit()
        
    except Exception as e:
        # Don't fail the main prediction if logging fails
        print(f"Warning: Failed to log prediction: {str(e)}")
        db.rollback()


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "H. pylori CDSS",
        "version": "1.0.0"
    }


@router.get("/version")
def get_version():
    """Get library versions and model configuration."""
    return {
        "service_version": "1.0.0",
        "python_version": sys.version,
        "scikit_learn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "models": {
            "screening_model": settings.SCREEN_MODEL_PATH,
            "staging_model": settings.STAGE_MODEL_PATH,
            "screening_threshold": settings.SCREEN_THRESH
        }
    }


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_single(
    case_input: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate recommendation for a single case.
    Automatically manages patient records - creates new or links to existing patient.
    Persists the case to database.
    """
    try:
        # Convert input to dict
        input_dict = case_input.dict(exclude_none=True)
        task = input_dict.get('task', 'screening')
        
        # Get or create patient record
        patient = get_or_create_patient(
            db=db,
            patient_id=case_input.patient_pseudo_id,
            full_name=case_input.patient_name,
            age=case_input.age,
            sex=case_input.sex,
            residence=case_input.residence,
            phone=case_input.patient_phone,
            email=case_input.patient_email,
            created_by=current_user.id
        )
        
        # Get ML predictions and recommendations (with timing)
        start_time = time.time()
        screen_prob, stage_pred, recommendations = get_recommendation(input_dict)
        prediction_time = time.time() - start_time
        
        # Create case record linked to patient
        new_case = Case(
            user_id=current_user.id,
            patient_db_id=patient.id,
            input_data=input_dict,
            case_type=task,
            screen_prob=screen_prob,
            stage_pred=stage_pred,
            recommendations=recommendations,
            patient_pseudo_id=patient.patient_id,  # Store the generated patient ID
            patient_name=patient.full_name,
            patient_phone=patient.phone,
            patient_email=patient.email
        )
        
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        
        # Log predictions for monitoring and retraining
        if screen_prob is not None:
            screening_prediction = "positive" if screen_prob >= settings.SCREEN_THRESH else "negative"
            log_prediction(
                db=db,
                model_name="screening",
                input_features=input_dict,
                prediction=screening_prediction,
                prediction_proba=screen_prob,
                user_id=current_user.id,
                case_id=new_case.id,
                patient_db_id=patient.id,
                prediction_time=prediction_time
            )
        
        if stage_pred is not None:
            log_prediction(
                db=db,
                model_name="staging",
                input_features=input_dict,
                prediction=stage_pred,
                user_id=current_user.id,
                case_id=new_case.id,
                patient_db_id=patient.id,
                prediction_time=prediction_time
            )
        
        return RecommendationResponse(
            screen_prob=screen_prob,
            stage_pred=stage_pred,
            recommendations=recommendations,
            input_data=input_dict,
            case_id=new_case.id
        )
    
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Error processing recommendation: {str(e)}"
        print(f"ERROR in /recommend: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/recommend/batch")
async def recommend_batch(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process batch recommendations from CSV upload.
    Persists all cases to database.
    Returns dict with total, processed count, and results list.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        results = []
        processed = 0
        failed = 0
        total_rows = len(df)
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Convert row to dict and remove NaN values
                input_dict = row.to_dict()
                input_dict = {k: v for k, v in input_dict.items() if pd.notna(v)}
                
                # Get predictions (with timing)
                start_time = time.time()
                screen_prob, stage_pred, recommendations = get_recommendation(input_dict)
                prediction_time = time.time() - start_time
                
                # Create case record
                new_case = Case(
                    user_id=current_user.id,
                    input_data=input_dict,
                    screen_prob=screen_prob,
                    stage_pred=stage_pred,
                    recommendations=recommendations,
                    patient_pseudo_id=input_dict.get('patient_pseudo_id')
                )
                
                db.add(new_case)
                db.commit()
                db.refresh(new_case)
                
                # Log predictions
                if screen_prob is not None:
                    screening_prediction = "positive" if screen_prob >= settings.SCREEN_THRESH else "negative"
                    log_prediction(
                        db=db,
                        model_name="screening",
                        input_features=input_dict,
                        prediction=screening_prediction,
                        prediction_proba=screen_prob,
                        user_id=current_user.id,
                        case_id=new_case.id,
                        prediction_time=prediction_time
                    )
                
                if stage_pred is not None:
                    log_prediction(
                        db=db,
                        model_name="staging",
                        input_features=input_dict,
                        prediction=stage_pred,
                        user_id=current_user.id,
                        case_id=new_case.id,
                        prediction_time=prediction_time
                    )
                
                results.append(RecommendationResponse(
                    screen_prob=screen_prob,
                    stage_pred=stage_pred,
                    recommendations=recommendations,
                    input_data=input_dict,
                    case_id=new_case.id
                ))
                
                processed += 1
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                failed += 1
                continue
        
        return {
            "total": total_rows,
            "processed": processed,
            "failed": failed,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch file: {str(e)}"
        )


@router.get("/cases")
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    case_type: Optional[str] = Query(None, description="Filter by case type (screening, staging)"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search patient name or ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk (low, moderate, high)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List cases with advanced filtering and pagination.
    
    Filters available:
    - patient_id: Filter by specific patient ID
    - case_type: screening or staging
    - start_date/end_date: Date range
    - search: Search in patient name or ID
    - risk_level: Filter by screening risk level
    
    Admins can see all cases, others see only their own.
    """
    # Build base query based on role
    query = db.query(Case).join(Patient, Case.patient_db_id == Patient.id, isouter=True)
    
    if current_user.role != "admin":
        query = query.filter(Case.user_id == current_user.id)
    
    # Apply filters
    if patient_id:
        query = query.filter(Case.patient_pseudo_id.ilike(f"%{patient_id}%"))
    
    if case_type:
        query = query.filter(Case.case_type == case_type)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Case.created_at >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Case.created_at <= end_dt)
        except ValueError:
            pass
    
    if search:
        query = query.filter(
            or_(
                Case.patient_pseudo_id.ilike(f"%{search}%"),
                Case.patient_name.ilike(f"%{search}%")
            )
        )
    
    if risk_level:
        # Filter by risk level based on screening probability
        if risk_level.lower() == "high":
            query = query.filter(Case.screen_prob >= 0.7)
        elif risk_level.lower() == "moderate":
            query = query.filter(and_(Case.screen_prob >= 0.4, Case.screen_prob < 0.7))
        elif risk_level.lower() == "low":
            query = query.filter(Case.screen_prob < 0.4)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply ordering and pagination
    offset = (page - 1) * page_size
    cases = query.order_by(Case.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Convert cases to proper format with enhanced information
    cases_data = []
    for case in cases:
        # Get clinician info
        clinician = db.query(User).filter(User.id == case.user_id).first()
        
        # Determine risk level
        risk = "unknown"
        if case.screen_prob is not None:
            if case.screen_prob >= 0.7:
                risk = "high"
            elif case.screen_prob >= 0.4:
                risk = "moderate"
            else:
                risk = "low"
        
        case_dict = {
            "id": case.id,
            "patient_id": case.patient_pseudo_id,
            "patient_name": case.patient_name,
            "user_id": case.user_id,
            "clinician_name": clinician.full_name if clinician else "Unknown",
            "case_type": case.case_type or case.input_data.get('task', 'unknown') if case.input_data else 'unknown',
            "input_data": case.input_data,
            "screen_prob": case.screen_prob,
            "stage_pred": case.stage_pred,
            "risk_level": risk,
            "recommendations": case.recommendations,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "is_approved": case.is_approved,
            "signed_at": case.signed_at.isoformat() if case.signed_at else None
        }
        cases_data.append(case_dict)
    
    return {
        "cases": cases_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        "filters_applied": {
            "patient_id": patient_id,
            "case_type": case_type,
            "start_date": start_date,
            "end_date": end_date,
            "search": search,
            "risk_level": risk_level
        }
    }


@router.get("/cases/{case_id}")
def get_case_detail(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information for a specific case.
    Users can only view their own cases unless they are admin.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this case"
        )
    
    # Return case data with proper formatting
    return {
        "id": case.id,
        "user_id": case.user_id,
        "input_data": case.input_data,
        "result": None,
        "recommendations": case.edited_recommendations or case.recommendations,
        "screen_prob": case.screen_prob,
        "stage_pred": case.stage_pred,
        "patient_name": case.patient_name,
        "patient_phone": case.patient_phone,
        "task": case.input_data.get('task', 'screening') if case.input_data else 'screening',
        "created_at": case.created_at,
        "updated_at": case.created_at
    }


@router.put("/cases/{case_id}")
def update_case(
    case_id: int,
    notes: Optional[str] = None,
    patient_name: Optional[str] = None,
    patient_phone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update case information.
    Users can update their own cases, admins can update any case.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this case"
        )
    
    # Update fields
    if notes is not None:
        case.notes = notes
    if patient_name is not None:
        case.patient_name = patient_name
    if patient_phone is not None:
        case.patient_phone = patient_phone
    
    db.commit()
    db.refresh(case)
    
    return {
        "message": "Case updated successfully",
        "case_id": case_id,
        "case": {
            "id": case.id,
            "patient_id": case.patient_pseudo_id,
            "patient_name": case.patient_name,
            "patient_phone": case.patient_phone,
            "notes": case.notes,
            "updated_at": datetime.utcnow().isoformat()
        }
    }


@router.delete("/cases/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific case.
    Users can only delete their own cases unless they are admin.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this case"
        )
    
    db.delete(case)
    db.commit()
    
    return {
        "message": "Case deleted successfully",
        "case_id": case_id
    }


@router.post("/cases/report")
def generate_cases_report(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive report of cases.
    Admin can see all cases, users can only see their own.
    """
    query = db.query(Case)
    
    # Filter by user if not admin
    if current_user.role != "admin":
        query = query.filter(Case.user_id == current_user.id)
    
    # Filter by date range if provided
    if start_date:
        query = query.filter(Case.created_at >= start_date)
    if end_date:
        query = query.filter(Case.created_at <= end_date)
    
    cases = query.all()
    
    # Generate statistics
    total_cases = len(cases)
    
    # Check both input_data['task'] AND case_type column for backward compatibility
    screening_cases = sum(1 for c in cases if (
        c.input_data.get('task') == "screening" or 
        c.case_type in ["screening", "symptom_assessment", "lab_screening"]
    ))
    staging_cases = sum(1 for c in cases if (
        c.input_data.get('task') == "staging" or 
        c.case_type in ["staging", "resistance_staging"]
    ))
    high_risk_cases = sum(1 for c in cases if c.screen_prob and c.screen_prob > 0.7)
    
    # Calculate average screening probability
    screening_probas = [c.screen_prob for c in cases if c.screen_prob is not None]
    avg_screening_proba = sum(screening_probas) / len(screening_probas) if screening_probas else 0
    
    return {
        "report_date": pd.Timestamp.now().isoformat(),
        "generated_by": current_user.email,
        "date_range": {
            "start": start_date or "all time",
            "end": end_date or "present"
        },
        "summary": {
            "total_cases": total_cases,
            "screening_cases": screening_cases,
            "staging_cases": staging_cases,
            "high_risk_cases": high_risk_cases,
            "average_screening_probability": round(avg_screening_proba, 3)
        },
        "cases": [
            {
                "id": case.id,
                "date": case.created_at.isoformat() if case.created_at else None,
                "task": case.input_data.get('task', 'unknown') if case.input_data else 'unknown',
                "patient_id": case.patient_pseudo_id,
                "screening_proba": case.screen_prob,
                "stage": case.stage_pred,
                "recommendations": case.recommendations
            }
            for case in cases
        ]
    }


@router.post("/ml/retrain")
def retrain_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrain ML models based on current case data.
    Only admins can trigger retraining.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can retrain models"
        )
    
    # Get all cases with complete data
    cases = db.query(Case).all()
    
    if len(cases) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough data to retrain models (minimum 10 cases required)"
        )
    
    # Prepare data for retraining
    screening_data = []
    staging_data = []
    
    for case in cases:
        task = case.input_data.get('task', 'unknown') if case.input_data else 'unknown'
        if task == "screening" and case.input_data:
            screening_data.append(case.input_data)
        elif task == "staging" and case.input_data:
            staging_data.append(case.input_data)
    
    return {
        "message": "Model retraining initiated",
        "status": "success",
        "data_summary": {
            "total_cases": len(cases),
            "screening_cases": len(screening_data),
            "staging_cases": len(staging_data)
        },
        "note": "Model retraining is a resource-intensive process. In production, this would be queued for background processing. For now, this endpoint validates data availability."
    }
