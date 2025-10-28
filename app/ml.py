"""Machine learning model loading and prediction logic."""
import joblib
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from app.config import settings


class MLModels:
    """Singleton class for lazy loading ML models."""
    
    _instance = None
    _screening_model = None
    _staging_model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModels, cls).__new__(cls)
        return cls._instance
    
    def load_screening_model(self):
        """Load the screening model (lazy loading)."""
        if self._screening_model is None:
            model_path = Path(settings.SCREEN_MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(f"Screening model not found at {settings.SCREEN_MODEL_PATH}")
            self._screening_model = joblib.load(model_path)
            print(f"[OK] Loaded screening model from {settings.SCREEN_MODEL_PATH}")
        return self._screening_model
    
    def load_staging_model(self) -> Optional[Any]:
        """Load the staging model (lazy loading, optional)."""
        if self._staging_model is None and settings.STAGE_MODEL_PATH:
            model_path = Path(settings.STAGE_MODEL_PATH)
            if model_path.exists():
                self._staging_model = joblib.load(model_path)
                print(f"[OK] Loaded staging model from {settings.STAGE_MODEL_PATH}")
            else:
                print(f"[WARNING] Staging model not found at {settings.STAGE_MODEL_PATH}, skipping")
        return self._staging_model


# Global instance
ml_models = MLModels()


def prepare_screening_features(input_data: Dict[str, Any]) -> pd.DataFrame:
    """Prepare features for screening model with proper defaults."""
    # All features expected by the model with sensible defaults
    data = {
        'age': [input_data.get('age', 45)],
        'sex': [1 if input_data.get('sex', 'M') == 'M' else 0],
        'residence': [1 if input_data.get('residence', 'urban') == 'urban' else 0],
        'sanitation': [input_data.get('sanitation', 1)],  # Assume good sanitation
        'water_source': [1 if input_data.get('water_source', 'clean') == 'clean' else 0],
        'crowding': [input_data.get('crowding', 0)],
        'poverty_index': [input_data.get('poverty_index', 0.3)],  # Medium poverty
        'smoking': [input_data.get('smoking', 0)],
        'nsaid_use': [input_data.get('nsaid_use', 0)],
        'prior_antibiotics_3m': [input_data.get('prior_antibiotics_3m', 0)],
        'epigastric_pain': [input_data.get('epigastric_pain', 0)],
        'nausea': [input_data.get('nausea', 0)],
        'bloating': [input_data.get('bloating', 0)],
        'early_satiety': [input_data.get('early_satiety', 0)],
        'weight_loss': [input_data.get('weight_loss', 0)],
        'stool_ag': [input_data.get('stool_ag', 0)],
        'stool_ab': [input_data.get('stool_ab', 0)],
        'hemoglobin': [input_data.get('hemoglobin', 13.0)],
        'crp': [input_data.get('crp', 3.0)],  # Normal CRP
        'wbc': [input_data.get('wbc', 7.0)]  # Normal WBC count
    }
    
    df = pd.DataFrame(data)
    return df


def prepare_staging_features(input_data: Dict[str, Any]) -> pd.DataFrame:
    """Prepare features for staging model."""
    # Calculate double_mut from individual mutations
    mut_A2143G = input_data.get('mut_A2143G', 0)
    mut_A2144G = input_data.get('mut_A2144G', 0)
    double_mut = 1 if (mut_A2143G == 1 and mut_A2144G == 1) else 0
    
    # Prepare all required features with defaults
    data = {
        'age': [input_data.get('age', 45)],  # Default age
        'sex': [1 if input_data.get('sex', 'M') == 'M' else 0],  # 1=Male, 0=Female  
        'mic_clari': [input_data.get('mic_clari', 0.5)],  # Default MIC value
        'mut_A2143G': [mut_A2143G],
        'mut_A2144G': [mut_A2144G], 
        'double_mut': [double_mut]
    }
    
    df = pd.DataFrame(data)
    return df


def has_staging_data(input_data: Dict[str, Any]) -> bool:
    """Check if input has sufficient staging features."""
    # Only require the key staging markers
    staging_keys = ['mic_clari', 'mut_A2143G', 'mut_A2144G']
    return any(input_data.get(key) is not None for key in staging_keys)


def predict_screening(input_data: Dict[str, Any]) -> float:
    """
    Predict H. pylori infection probability with calibration adjustment.
    
    Returns:
        Probability of H. pylori infection (0-1)
    """
    model = ml_models.load_screening_model()
    features = prepare_screening_features(input_data)
    
    # Get probability of positive class
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(features)[0]
        # Assuming binary classification: [neg_prob, pos_prob]
        raw_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
        
        # Apply probability smoothing to avoid extreme predictions
        # This helps with overconfident models
        # Smooth extreme values towards more reasonable clinical ranges
        if raw_prob < 0.05:
            # Very low risk -> map to 5-15% range
            adjusted_prob = 0.05 + (raw_prob / 0.05) * 0.10
        elif raw_prob > 0.95:
            # Very high risk -> map to 85-95% range
            adjusted_prob = 0.85 + ((raw_prob - 0.95) / 0.05) * 0.10
        else:
            # Middle range -> apply slight smoothing
            adjusted_prob = 0.1 + (raw_prob * 0.8)
        
        return float(adjusted_prob)
    else:
        # Fallback to predict if predict_proba not available
        prediction = model.predict(features)[0]
        return float(prediction)


def predict_staging(input_data: Dict[str, Any]) -> Optional[str]:
    """
    Predict resistance stage (low, moderate, high) with clinical MIC interpretation.
    
    Returns:
        Stage prediction or None if model not available or insufficient data
    """
    staging_model = ml_models.load_staging_model()
    
    if staging_model is None:
        return None
    
    if not has_staging_data(input_data):
        return None
    
    # First check clinical MIC breakpoints (overrides ML if available)
    mic_clari = input_data.get('mic_clari')
    if mic_clari is not None:
        if mic_clari <= 0.25:
            return "low"  # Sensitive
        elif mic_clari <= 1.0:
            return "moderate"  # Intermediate  
        else:
            return "high"  # Resistant
    
    # Fallback to ML model if no MIC available
    features = prepare_staging_features(input_data)
    
    if features.empty:
        return None
    
    try:
        prediction = staging_model.predict(features)[0]
        
        # Map numeric predictions to labels if needed
        if isinstance(prediction, (int, float)):
            stage_map = {0: "low", 1: "moderate", 2: "high"}
            return stage_map.get(int(prediction), "unknown")
        
        return str(prediction).lower()
    except Exception as e:
        print(f"Error in staging prediction: {e}")
        return None


def generate_recommendations(
    screen_prob: Optional[float],
    stage_pred: Optional[str],
    input_data: Dict[str, Any]
) -> List[str]:
    """
    Generate detailed clinical recommendations based on predictions.
    
    Args:
        screen_prob: Screening probability (0-1)
        stage_pred: Stage prediction (low, moderate, high, or None)
        input_data: Original input data
    
    Returns:
        List of detailed recommendation paragraphs
    """
    recommendations = []
    threshold = settings.SCREEN_THRESH
    
    # Screening recommendations with detailed paragraphs
    if screen_prob is not None:
        if screen_prob >= threshold:
            recommendations.append(
                f"INFECTION RISK ASSESSMENT (High Risk - {screen_prob:.1%}): "
                f"Based on the clinical presentation and screening model analysis, this patient demonstrates "
                f"a {screen_prob:.1%} probability of active H. pylori infection. This elevated risk warrants immediate "
                f"attention and confirmatory testing. The combination of presenting symptoms and risk factors "
                f"strongly suggests active infection. Recommend proceeding with definitive diagnostic workup including "
                f"upper endoscopy with biopsy for histological confirmation and culture-based antibiotic susceptibility "
                f"testing. Consider ordering urea breath test or stool antigen test as alternative non-invasive "
                f"confirmation methods. Initiate patient education regarding H. pylori transmission, complications, "
                f"and importance of treatment adherence."
            )
        elif screen_prob >= 0.4:
            recommendations.append(
                f"INFECTION RISK ASSESSMENT (Moderate Risk - {screen_prob:.1%}): "
                f"The screening analysis indicates a {screen_prob:.1%} probability of H. pylori infection, placing "
                f"this patient in the moderate risk category. While not immediately critical, this level of risk "
                f"warrants further investigation to rule out active infection. Clinical symptoms and patient history "
                f"suggest possible gastric involvement that should be evaluated more thoroughly. Recommend non-invasive "
                f"diagnostic testing such as urea breath test (C13 or C14) or stool antigen test to confirm or exclude "
                f"infection. Consider serology (IgG antibody test) if other tests are contraindicated, though note that "
                f"serology cannot distinguish active from past infection. Schedule follow-up in 2-4 weeks to review test "
                f"results and determine treatment plan if positive. Provide lifestyle counseling including dietary "
                f"modifications to reduce gastric irritation."
            )
        else:
            recommendations.append(
                f"INFECTION RISK ASSESSMENT (Low Risk - {screen_prob:.1%}): "
                f"The screening model estimates a {screen_prob:.1%} probability of H. pylori infection, indicating "
                f"low clinical risk at this time. While active infection appears unlikely based on current presentation, "
                f"it is important to monitor the patient's symptom progression and maintain clinical vigilance. If "
                f"gastrointestinal symptoms persist or worsen over the next 4-8 weeks, consider re-evaluation with "
                f"non-invasive testing (urea breath test or stool antigen). Provide symptomatic management for any "
                f"presenting complaints including dyspepsia, nausea, or mild abdominal discomfort. Recommend lifestyle "
                f"modifications including stress reduction, avoidance of NSAIDs and alcohol, and dietary adjustments. "
                f"Educate patient on warning signs that would warrant immediate medical attention including severe "
                f"abdominal pain, persistent vomiting, blood in stool (melena or hematochezia), or unintentional "
                f"weight loss. Schedule routine follow-up in 3-6 months or sooner if symptoms change."
            )
    
    # Staging and treatment recommendations
    if stage_pred:
        if stage_pred == "low":
            recommendations.append(
                "TREATMENT RECOMMENDATION (Low Antibiotic Resistance): "
                "Based on resistance profiling, this patient is suitable for standard first-line triple therapy. "
                "Prescribe the following 14-day regimen: Proton Pump Inhibitor (PPI) - Omeprazole 20mg or "
                "Esomeprazole 40mg twice daily, Amoxicillin 1000mg twice daily, and Clarithromycin 500mg twice daily. "
                "All medications should be taken together with meals to optimize absorption and minimize gastrointestinal "
                "side effects. Counsel patient on importance of completing full 14-day course even if symptoms resolve "
                "earlier. Common side effects include diarrhea (20-30%), nausea, and metallic taste from clarithromycin. "
                "Schedule test-of-cure (urea breath test or stool antigen) 4-6 weeks after completion of therapy to "
                "confirm eradication. Expected eradication rate with this regimen is 85-90% in low-resistance populations."
            )
        elif stage_pred == "moderate":
            recommendations.append(
                "TREATMENT RECOMMENDATION (Moderate Antibiotic Resistance): "
                "Resistance profiling suggests moderate clarithromycin resistance, which may reduce the efficacy of "
                "standard triple therapy. Consider initiating standard triple therapy (PPI + Amoxicillin + Clarithromycin "
                "for 14 days) while acknowledging reduced eradication rates (60-75%). Alternative first-line option: "
                "Bismuth-based quadruple therapy for 10-14 days (PPI + Bismuth subcitrate 120-300mg four times daily + "
                "Tetracycline 500mg four times daily + Metronidazole 500mg three times daily). This regimen is less "
                "affected by clarithromycin resistance and maintains 75-85% eradication rates. Mandatory test-of-cure "
                "at 4-6 weeks post-treatment. If eradication fails with triple therapy, switch to bismuth quadruple "
                "therapy or levofloxacin-based triple therapy as rescue therapy. Consider gastroenterology consultation "
                "if symptoms are severe or if patient has failed prior eradication attempts."
            )
        elif stage_pred == "high":
            recommendations.append(
                "TREATMENT RECOMMENDATION (High Antibiotic Resistance - Specialist Referral Required): "
                "Resistance analysis indicates high-level clarithromycin resistance with possible multi-drug resistance. "
                "Standard triple therapy is NOT recommended due to unacceptably low eradication rates (<50%). "
                "URGENT gastroenterology referral is required for specialist evaluation and culture-guided therapy. "
                "Consider empiric bismuth-based quadruple therapy while awaiting specialist consultation: PPI twice "
                "daily + Bismuth subcitrate + Tetracycline + Metronidazole for 14 days. Alternative: Levofloxacin-based "
                "triple therapy (PPI + Amoxicillin + Levofloxacin) for 10-14 days if fluoroquinolone resistance is unlikely. "
                "High-resistance cases may require culture-based antibiotic susceptibility testing via endoscopic biopsy "
                "to guide personalized therapy. Emphasize to patient the critical importance of treatment adherence and "
                "avoiding antibiotic monotherapy which can worsen resistance. Mandatory test-of-cure and consider repeat "
                "endoscopy if eradication fails to rule out complications including gastric atrophy or intestinal metaplasia."
            )
    
    # Alarm symptoms assessment
    has_alarm_symptoms = any([
        input_data.get('weight_loss'),
        input_data.get('hemoglobin', 100) < 10  # Anemia threshold
    ])
    
    if has_alarm_symptoms:
        recommendations.append(
            "ALARM SYMPTOMS DETECTED - URGENT ACTION REQUIRED: "
            "This patient presents with concerning alarm features including unintentional weight loss and/or "
            "significant anemia (hemoglobin <10 g/dL). These findings raise suspicion for complicated peptic ulcer "
            "disease, gastric malignancy, or severe chronic gastritis with atrophic changes. URGENT gastroenterology "
            "referral is mandated within 2 weeks (ideally within 1 week) for upper endoscopy with multiple biopsies "
            "to evaluate for malignancy, severe dysplasia, or intestinal metaplasia. Do NOT delay endoscopy for "
            "H. pylori testing or treatment. If patient presents with acute severe symptoms (hematemesis, melena, "
            "severe abdominal pain), arrange immediate emergency department evaluation to rule out active gastrointestinal "
            "bleeding or perforation. Consider CBC, iron studies, and vitamin B12/folate levels to characterize anemia. "
            "Initiate PPI therapy (high-dose: 40mg twice daily) immediately while awaiting endoscopy."
        )
    
    # Professional disclaimer
    recommendations.append(
        "CLINICAL DECISION SUPPORT DISCLAIMER: "
        "The recommendations provided by this clinical decision support system are generated using AI-powered "
        "predictive models trained on epidemiological and clinical data. These recommendations are intended to "
        "assist, not replace, professional clinical judgment. The treating clinician retains full responsibility "
        "for all diagnostic and therapeutic decisions, including consideration of patient-specific factors, "
        "contraindications, drug interactions, and local resistance patterns. Always correlate AI-generated "
        "recommendations with clinical assessment, patient preferences, and current evidence-based guidelines. "
        "This system does not establish a doctor-patient relationship and should not be used as the sole basis "
        "for patient care decisions. For questions or concerns regarding these recommendations, consult with "
        "gastroenterology or infectious disease specialists."
    )
    
    return recommendations


def get_recommendation(input_data: Dict[str, Any]) -> Tuple[Optional[float], Optional[str], List[str]]:
    """
    Main function to get complete recommendation.
    
    Returns:
        Tuple of (screen_prob, stage_pred, recommendations)
    """
    # Get screening prediction
    screen_prob = None
    try:
        screen_prob = predict_screening(input_data)
    except Exception as e:
        print(f"Error in screening prediction: {e}")
    
    # Get staging prediction (if data available)
    stage_pred = None
    try:
        if has_staging_data(input_data):
            stage_pred = predict_staging(input_data)
    except Exception as e:
        print(f"Error in staging prediction: {e}")
    
    # Generate recommendations
    recommendations = generate_recommendations(screen_prob, stage_pred, input_data)
    
    return screen_prob, stage_pred, recommendations
