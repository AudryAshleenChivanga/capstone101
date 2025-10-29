"""
Multi-Stage Clinical Workflow Routes for H. pylori CDSS
Implements 3-stage assessment: Symptom → Lab → RIC
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel

from app.db import get_db
from app.models import Case, Patient, User
from app.routes_auth import get_current_user
from app.utils.patient_utils import get_or_create_patient
from app.ml_models import symptom_model, lab_screening_model, ric_staging_model

# Initialize router
router = APIRouter(prefix="/workflow", tags=["workflow"])

# Note: Using rule-based assessment - ML models can be added later


# Pydantic models
class Stage1SymptomAssessment(BaseModel):
    # Patient demographics
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    residence: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Symptoms (binary 0/1)
    abdominal_pain: Optional[int] = 0
    bloating: Optional[int] = 0
    nausea: Optional[int] = 0
    vomiting: Optional[int] = 0
    heartburn: Optional[int] = 0
    indigestion: Optional[int] = 0
    loss_of_appetite: Optional[int] = 0
    weight_loss: Optional[int] = 0
    black_stool: Optional[int] = 0
    blood_in_vomit: Optional[int] = 0
    persistent_pain: Optional[int] = 0
    
    # Risk factors
    family_history_gastric: Optional[int] = 0
    previous_ulcer: Optional[int] = 0
    nsaid_use: Optional[int] = 0
    smoking: Optional[int] = 0
    
    # Duration
    symptom_duration_weeks: Optional[int] = 0


class Stage2LabScreening(BaseModel):
    patient_id: str  # HP-2025-XXXX (required - from Stage 1)
    case_id: int  # Stage 1 case ID
    
    # Lab test results
    stool_antigen: Optional[str] = None  # positive/negative
    hp_igg: Optional[str] = None  # positive/negative
    hemoglobin: Optional[float] = None
    crp: Optional[float] = None
    wbc: Optional[float] = None
    
    # Additional markers
    esr: Optional[float] = None
    platelet_count: Optional[float] = None


class Stage3RICStaging(BaseModel):
    patient_id: str  # HP-2025-XXXX (required - from Stage 1/2)
    case_id: int  # Stage 2 case ID
    
    # Antibiotic resistance markers (MIC values)
    mic_clarithromycin: Optional[float] = None  # MIC for clarithromycin
    mic_metronidazole: Optional[float] = None  # MIC for metronidazole
    mic_levofloxacin: Optional[float] = None  # MIC for levofloxacin
    
    # Genetic mutations (23S rRNA for clarithromycin resistance)
    mutation_a2143g: Optional[int] = 0  # A2143G mutation
    mutation_a2144g: Optional[int] = 0  # A2144G mutation (note: was A2142G in some sources)
    
    # Additional mutations for other antibiotics
    mutation_rdxa: Optional[int] = 0  # rdxA mutation (metronidazole resistance)
    mutation_gyra: Optional[int] = 0  # gyrA mutation (fluoroquinolone resistance)


@router.post("/stage1/symptom-assessment")
def stage1_symptom_assessment(
    data: Stage1SymptomAssessment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stage 1: Symptom-Based Assessment
    
    Evaluates patient symptoms during registration to:
    1. Determine gastric disease risk level
    2. Recommend appropriate lab tests
    3. Create patient record and initial case
    
    Returns assessment with recommended tests and whether to proceed to Stage 2.
    """
    
    # Get or create patient
    patient = get_or_create_patient(
        db=db,
        patient_id=data.patient_id,
        full_name=data.patient_name,
        age=data.age,
        sex=data.sex,
        residence=data.residence,
        phone=data.phone,
        email=data.email,
        created_by=current_user.id
    )
    
    # Prepare symptom data for ML model
    symptom_data = {
        'age': data.age or 0,
        'sex': data.sex or '',
        'abdominal_pain': data.abdominal_pain,
        'bloating': data.bloating,
        'nausea': data.nausea,
        'vomiting': data.vomiting,
        'heartburn': data.heartburn,
        'indigestion': data.indigestion,
        'loss_of_appetite': data.loss_of_appetite,
        'weight_loss': data.weight_loss,
        'black_stool': data.black_stool,
        'blood_in_vomit': data.blood_in_vomit,
        'persistent_pain': data.persistent_pain,
        'family_history_gastric': data.family_history_gastric,
        'previous_ulcer': data.previous_ulcer,
        'nsaid_use': data.nsaid_use,
        'smoking': data.smoking,
        'symptom_duration_weeks': data.symptom_duration_weeks
    }
    
    # Run symptom assessment model
    assessment = symptom_model.assess_symptoms(symptom_data)
    
    # Create Stage 1 case
    new_case = Case(
        user_id=current_user.id,
        patient_db_id=patient.id,
        workflow_stage="stage1_symptom",
        case_type="symptom_assessment",
        input_data=symptom_data,
        stage1_assessment=assessment,
        symptom_risk_level=assessment['risk_level'],
        lab_recommendation=", ".join(assessment['recommended_tests']),
        recommendations=assessment['recommendations'],
        patient_pseudo_id=patient.patient_id,
        patient_name=patient.full_name,
        patient_phone=patient.phone,
        patient_email=patient.email
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    return {
        "success": True,
        "stage": "stage1_symptom",
        "patient_id": patient.patient_id,
        "case_id": new_case.id,
        "assessment": {
            "risk_level": assessment['risk_level'],
            "risk_probability": assessment['risk_probability'],
            "confidence": assessment['confidence'],
            "alarm_symptoms": assessment.get('alarm_symptoms', []),
            "recommended_tests": assessment['recommended_tests'],
            "recommendations": assessment['recommendations'],
            "proceed_to_stage2": assessment['proceed_to_stage2']
        },
        "next_steps": {
            "stage": "stage2_lab",
            "action": "Perform recommended laboratory tests" if assessment['proceed_to_stage2'] else "Monitor symptoms",
            "required_tests": assessment['recommended_tests'] if assessment['proceed_to_stage2'] else []
        }
    }


@router.post("/stage2/lab-screening")
def stage2_lab_screening(
    data: Stage2LabScreening,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stage 2: Laboratory-Based Screening
    
    Processes lab test results (antibody, serology, biomarkers) to:
    1. Confirm H. pylori infection
    2. Assess infection severity
    3. Determine if staging (Stage 3) is needed
    
    Requires patient_id and case_id from Stage 1.
    """
    
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found. Please complete Stage 1 first.")
    
    # Get Stage 1 case
    stage1_case = db.query(Case).filter(
        Case.id == data.case_id,
        Case.patient_db_id == patient.id,
        Case.workflow_stage == "stage1_symptom"
    ).first()
    
    if not stage1_case:
        raise HTTPException(
            status_code=404,
            detail="Stage 1 assessment not found. Please complete symptom assessment first."
        )
    
    # Prepare comprehensive data for screening model (needs patient demographics + symptoms + lab results)
    # Get Stage 1 input data for patient demographics and symptoms
    stage1_input = stage1_case.input_data if isinstance(stage1_case.input_data, dict) else {}
    
    # Combine with lab results for complete feature set
    lab_data = {
        # Patient demographics (from Stage 1)
        'age': patient.age or stage1_input.get('age', 45),
        'sex': patient.sex or stage1_input.get('sex', 'M'),
        'residence': patient.residence or stage1_input.get('residence', 'urban'),
        
        # Risk factors (from Stage 1 or defaults)
        'smoking': stage1_input.get('smoking', 0),
        'nsaid_use': stage1_input.get('nsaid_use', 0),
        'sanitation': stage1_input.get('sanitation', 1),
        'water_source': stage1_input.get('water_source', 'clean'),
        'crowding': stage1_input.get('crowding', 0),
        'poverty_index': stage1_input.get('poverty_index', 0.3),
        'prior_antibiotics_3m': stage1_input.get('prior_antibiotics_3m', 0),
        
        # Symptoms (from Stage 1)
        'epigastric_pain': stage1_input.get('abdominal_pain', 0),
        'nausea': stage1_input.get('nausea', 0),
        'bloating': stage1_input.get('bloating', 0),
        'early_satiety': stage1_input.get('loss_of_appetite', 0),
        'weight_loss': stage1_input.get('weight_loss', 0),
        
        # Lab test results (from Stage 2 input)
        'stool_ag': 1 if data.stool_antigen == 'positive' else 0,
        'stool_ab': 1 if data.hp_igg == 'positive' else 0,
        'hemoglobin': data.hemoglobin,
        'crp': data.crp,
        'wbc': data.wbc,
        
        # Additional lab data for case record
        'stool_antigen': data.stool_antigen,
        'hp_igg': data.hp_igg,
        'esr': data.esr,
        'platelet_count': data.platelet_count
    }
    
    # Run lab screening model
    try:
        screening_result = lab_screening_model.screen(lab_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lab screening model error: {str(e)}")
    
    # Create Stage 2 case
    new_case = Case(
        user_id=current_user.id,
        patient_db_id=patient.id,
        workflow_stage="stage2_lab",
        case_type="lab_screening",
        input_data=lab_data,
        stage2_lab_results=lab_data,
        screen_prob=screening_result['infection_probability'],
        recommendations=screening_result['recommendations'],
        patient_pseudo_id=patient.patient_id,
        patient_name=patient.full_name,
        patient_phone=patient.phone,
        patient_email=patient.email
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    return {
        "success": True,
        "stage": "stage2_lab",
        "patient_id": patient.patient_id,
        "case_id": new_case.id,
        "stage1_case_id": stage1_case.id,
        "screening_result": {
            "infection_probability": screening_result['infection_probability'],
            "status": screening_result['status'],
            "confidence": screening_result['confidence'],
            "recommendations": screening_result['recommendations'],
            "proceed_to_stage3": screening_result['proceed_to_stage3']
        },
        "next_steps": {
            "stage": "stage3_ric" if screening_result['proceed_to_stage3'] else "treatment",
            "action": "Perform RIC staging" if screening_result['proceed_to_stage3'] else "Begin treatment protocol",
            "rationale": "H. pylori infection confirmed - staging required" if screening_result['proceed_to_stage3'] else "No infection detected or inconclusive"
        }
    }


@router.post("/stage3/ric-staging")
def stage3_ric_staging(
    data: Stage3RICStaging,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stage 3: Antibiotic Resistance Staging & Treatment Selection
    
    Determines antibiotic resistance level and selects appropriate treatment based on:
    1. MIC (Minimum Inhibitory Concentration) values for key antibiotics
    2. Genetic mutations (23S rRNA, rdxA, gyrA)
    3. Patient demographics and clinical context
    
    Note: This stage may recommend endoscopy with biopsy for culture-based 
    susceptibility testing if resistance patterns are unclear or concerning.
    
    Requires patient_id and case_id from Stage 2.
    Returns detailed treatment protocol tailored to resistance profile.
    """
    
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get Stage 2 case
    stage2_case = db.query(Case).filter(
        Case.id == data.case_id,
        Case.patient_db_id == patient.id,
        Case.workflow_stage == "stage2_lab"
    ).first()
    
    if not stage2_case:
        raise HTTPException(
            status_code=404,
            detail="Stage 2 lab screening not found. Please complete lab tests first."
        )
    
    # Prepare staging data (antibiotic resistance markers)
    # Primary marker: clarithromycin MIC (most important for treatment selection)
    mic_clari = data.mic_clarithromycin if data.mic_clarithromycin is not None else 0.5
    
    staging_data = {
        # Patient demographics
        'age': patient.age or 40,
        'sex': patient.sex or 'M',
        
        # Antibiotic resistance markers
        'mic_clari': mic_clari,  # Clarithromycin MIC (most critical)
        'mut_A2143G': data.mutation_a2143g,  # 23S rRNA mutation
        'mut_A2144G': data.mutation_a2144g,  # Alternative notation: A2142G
        
        # Additional data for case record
        'mic_metronidazole': data.mic_metronidazole,
        'mic_levofloxacin': data.mic_levofloxacin,
        'mutation_rdxa': data.mutation_rdxa,
        'mutation_gyra': data.mutation_gyra
    }
    
    # Run antibiotic resistance staging model
    try:
        staging_result = ric_staging_model.stage_disease(staging_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Staging model error: {str(e)}")
    
    # Create Stage 3 case
    new_case = Case(
        user_id=current_user.id,
        patient_db_id=patient.id,
        workflow_stage="stage3_ric",
        case_type="resistance_staging",
        input_data=staging_data,
        stage3_ric_values=staging_data,
        stage_pred=staging_result['stage'],
        recommendations=[
            f"Antibiotic resistance level: {staging_result['stage']}", 
            f"Treatment protocol: {staging_result['treatment_protocol']['regimen']}"
        ],
        patient_pseudo_id=patient.patient_id,
        patient_name=patient.full_name,
        patient_phone=patient.phone,
        patient_email=patient.email
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    return {
        "success": True,
        "stage": "stage3_ric",
        "patient_id": patient.patient_id,
        "case_id": new_case.id,
        "stage2_case_id": stage2_case.id,
        "staging_result": {
            "stage": staging_result['stage'],
            "stage_confidence": staging_result['stage_confidence'],
            "stage_probabilities": staging_result['stage_probabilities'],
            "biopsy_recommended": staging_result['biopsy_recommended'],
            "treatment_protocol": staging_result['treatment_protocol']
        },
        "treatment_ready": True,
        "prescription_data": {
            "diagnosis": f"H. pylori infection - {staging_result['stage']} severity",
            "medications": staging_result['treatment_protocol']['medications'],
            "recommendations": "\n".join(staging_result['treatment_protocol'].get('lifestyle', [])),
            "follow_up": staging_result['treatment_protocol']['follow_up'],
            "stage": "stage3_ric",
            "protocol_type": staging_result['treatment_protocol']['regimen']
        }
    }


@router.get("/patient/{patient_id}/journey")
def get_patient_journey(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete patient journey across all stages.
    
    Returns timeline of assessments from Stage 1 → Stage 2 → Stage 3
    with all results and recommendations.
    """
    
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all cases for this patient
    cases = db.query(Case).filter(
        Case.patient_db_id == patient.id
    ).order_by(Case.created_at).all()
    
    # Organize by stage
    journey = {
        "patient_id": patient.patient_id,
        "patient_name": patient.full_name,
        "stages": [],
        "current_stage": None,
        "completed_stages": []
    }
    
    for case in cases:
        stage_info = {
            "case_id": case.id,
            "stage": case.workflow_stage,
            "case_type": case.case_type,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "clinician": db.query(User).filter(User.id == case.user_id).first().full_name if case.user_id else "Unknown"
        }
        
        if case.workflow_stage == "stage1_symptom":
            stage_info.update({
                "risk_level": case.symptom_risk_level,
                "recommended_tests": case.lab_recommendation,
                "assessment": case.stage1_assessment
            })
        elif case.workflow_stage == "stage2_lab":
            stage_info.update({
                "infection_probability": case.screen_prob,
                "lab_results": case.stage2_lab_results
            })
        elif case.workflow_stage == "stage3_ric":
            stage_info.update({
                "severity": case.stage_pred,
                "ric_values": case.stage3_ric_values
            })
        
        journey["stages"].append(stage_info)
        journey["completed_stages"].append(case.workflow_stage)
    
    # Determine current stage
    if cases:
        last_case = cases[-1]
        if last_case.workflow_stage == "stage1_symptom":
            journey["current_stage"] = "stage2_lab"
            journey["next_action"] = "Complete laboratory tests"
        elif last_case.workflow_stage == "stage2_lab":
            journey["current_stage"] = "stage3_ric"
            journey["next_action"] = "Perform RIC staging if H. pylori positive"
        elif last_case.workflow_stage == "stage3_ric":
            journey["current_stage"] = "treatment"
            journey["next_action"] = "Generate prescription and begin treatment"
    
    return journey


@router.get("/statistics")
def get_workflow_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics on workflow completion and patient progression."""
    
    # Count cases by stage
    stage1_count = db.query(Case).filter(Case.workflow_stage == "stage1_symptom").count()
    stage2_count = db.query(Case).filter(Case.workflow_stage == "stage2_lab").count()
    stage3_count = db.query(Case).filter(Case.workflow_stage == "stage3_ric").count()
    
    # Count patients with completed workflows
    patients_with_stage3 = db.query(Case.patient_db_id).filter(
        Case.workflow_stage == "stage3_ric"
    ).distinct().count()
    
    return {
        "total_patients": db.query(Patient).count(),
        "stage_distribution": {
            "stage1_symptom": stage1_count,
            "stage2_lab": stage2_count,
            "stage3_ric": stage3_count
        },
        "completion_metrics": {
            "patients_completed_full_workflow": patients_with_stage3,
            "stage1_to_stage2_conversion": f"{(stage2_count/stage1_count*100):.1f}%" if stage1_count > 0 else "0%",
            "stage2_to_stage3_conversion": f"{(stage3_count/stage2_count*100):.1f}%" if stage2_count > 0 else "0%"
        }
    }

