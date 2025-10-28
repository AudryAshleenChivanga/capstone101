"""
Enhanced Machine Learning Models for Multi-Stage H. pylori CDSS
Includes: Symptom Assessment, Lab Screening, RIC Staging, and Model Retraining
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from typing import Dict, Tuple, Optional, List
import json


class SymptomAssessmentModel:
    """
    Stage 1: Symptom-Based Assessment Model
    Evaluates patient symptoms during registration to determine gastric disease risk
    and recommend appropriate lab tests.
    """
    
    def __init__(self, model_path=None):
        """Initialize the symptom assessment model."""
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or "models/symptom_assessment.joblib"
        self.feature_names = [
            'age', 'sex_encoded',  # Demographics
            'abdominal_pain', 'bloating', 'nausea', 'vomiting',  # Upper GI symptoms
            'heartburn', 'indigestion', 'loss_of_appetite', 'weight_loss',  # Common symptoms
            'black_stool', 'blood_in_vomit', 'persistent_pain',  # Alarm symptoms
            'family_history', 'previous_ulcer', 'nsaid_use', 'smoking',  # Risk factors
            'symptom_duration_weeks'  # Duration
        ]
        
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
    
    def prepare_features(self, patient_data: Dict) -> np.ndarray:
        """Convert patient symptom data to feature vector."""
        features = []
        
        # Demographics
        features.append(patient_data.get('age', 0))
        features.append(1 if patient_data.get('sex', '').lower() in ['male', 'm'] else 0)
        
        # Symptoms (binary: 0 or 1)
        symptom_keys = [
            'abdominal_pain', 'bloating', 'nausea', 'vomiting',
            'heartburn', 'indigestion', 'loss_of_appetite', 'weight_loss',
            'black_stool', 'blood_in_vomit', 'persistent_pain'
        ]
        for key in symptom_keys:
            features.append(int(patient_data.get(key, 0)))
        
        # Risk factors
        features.append(int(patient_data.get('family_history_gastric', 0)))
        features.append(int(patient_data.get('previous_ulcer', 0)))
        features.append(int(patient_data.get('nsaid_use', 0)))
        features.append(int(patient_data.get('smoking', 0)))
        
        # Symptom duration
        features.append(patient_data.get('symptom_duration_weeks', 0))
        
        return np.array(features).reshape(1, -1)
    
    def assess_symptoms(self, patient_data: Dict) -> Dict:
        """
        Assess patient symptoms and provide recommendations.
        
        Returns:
            Dict with risk_level, confidence, recommended_tests, and recommendations
        """
        if self.model is None:
            return self._rule_based_assessment(patient_data)
        
        # Prepare features
        X = self.prepare_features(patient_data)
        X_scaled = self.scaler.transform(X)
        
        # Get prediction
        risk_prob = self.model.predict_proba(X_scaled)[0][1]  # Probability of high risk
        
        # Determine risk level
        if risk_prob >= 0.7:
            risk_level = "high"
            recommended_tests = ["H. pylori Stool Antigen", "H. pylori Serology (IgG)", "Complete Blood Count", "Endoscopy"]
        elif risk_prob >= 0.4:
            risk_level = "moderate"
            recommended_tests = ["H. pylori Stool Antigen", "H. pylori Serology (IgG)", "Complete Blood Count"]
        else:
            risk_level = "low"
            recommended_tests = ["H. pylori Stool Antigen", "Complete Blood Count"]
        
        # Check for alarm symptoms
        alarm_symptoms = []
        if patient_data.get('black_stool'): alarm_symptoms.append("black stool (melena)")
        if patient_data.get('blood_in_vomit'): alarm_symptoms.append("blood in vomit (hematemesis)")
        if patient_data.get('weight_loss'): alarm_symptoms.append("unexplained weight loss")
        if patient_data.get('persistent_pain'): alarm_symptoms.append("persistent severe pain")
        
        if alarm_symptoms:
            risk_level = "high"
            recommended_tests.append("Urgent Endoscopy")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, alarm_symptoms, patient_data)
        
        return {
            "risk_level": risk_level,
            "risk_probability": float(risk_prob),
            "confidence": float(max(risk_prob, 1 - risk_prob)),
            "recommended_tests": recommended_tests,
            "alarm_symptoms": alarm_symptoms,
            "recommendations": recommendations,
            "proceed_to_stage2": risk_level in ["moderate", "high"]
        }
    
    def _rule_based_assessment(self, patient_data: Dict) -> Dict:
        """Fallback rule-based assessment if model not trained."""
        score = 0
        alarm_symptoms = []
        
        # Alarm symptoms - immediate high risk
        if patient_data.get('black_stool'): 
            score += 5
            alarm_symptoms.append("black stool (melena)")
        if patient_data.get('blood_in_vomit'): 
            score += 5
            alarm_symptoms.append("blood in vomit (hematemesis)")
        if patient_data.get('weight_loss'): 
            score += 3
            alarm_symptoms.append("unexplained weight loss")
        if patient_data.get('persistent_pain'): 
            score += 3
            alarm_symptoms.append("persistent severe pain")
        
        # Common symptoms
        if patient_data.get('abdominal_pain'): score += 1
        if patient_data.get('bloating'): score += 1
        if patient_data.get('nausea'): score += 1
        if patient_data.get('heartburn'): score += 1
        if patient_data.get('indigestion'): score += 1
        if patient_data.get('loss_of_appetite'): score += 2
        
        # Risk factors
        if patient_data.get('family_history_gastric'): score += 2
        if patient_data.get('previous_ulcer'): score += 2
        if patient_data.get('nsaid_use'): score += 1
        if patient_data.get('smoking'): score += 1
        if patient_data.get('age', 0) > 50: score += 1
        
        # Symptom duration
        duration = patient_data.get('symptom_duration_weeks', 0)
        if duration > 8: score += 2
        elif duration > 4: score += 1
        
        # Determine risk level
        if score >= 8 or alarm_symptoms:
            risk_level = "high"
            recommended_tests = ["H. pylori Stool Antigen", "H. pylori Serology (IgG)", "Complete Blood Count", "Endoscopy"]
        elif score >= 4:
            risk_level = "moderate"
            recommended_tests = ["H. pylori Stool Antigen", "H. pylori Serology (IgG)", "Complete Blood Count"]
        else:
            risk_level = "low"
            recommended_tests = ["H. pylori Stool Antigen"]
        
        recommendations = self._generate_recommendations(risk_level, alarm_symptoms, patient_data)
        
        return {
            "risk_level": risk_level,
            "risk_probability": min(score / 15.0, 1.0),
            "confidence": 0.75,
            "recommended_tests": recommended_tests,
            "alarm_symptoms": alarm_symptoms,
            "recommendations": recommendations,
            "proceed_to_stage2": risk_level in ["moderate", "high"]
        }
    
    def _generate_recommendations(self, risk_level: str, alarm_symptoms: List, patient_data: Dict) -> List[str]:
        """Generate clinical recommendations based on assessment."""
        recommendations = []
        
        if alarm_symptoms:
            recommendations.append("⚠️ URGENT: Alarm symptoms detected. Immediate evaluation required.")
            recommendations.append("Refer for urgent endoscopy within 2 weeks.")
        
        if risk_level == "high":
            recommendations.append("High suspicion of H. pylori infection or gastric pathology.")
            recommendations.append("Proceed with comprehensive laboratory testing.")
            recommendations.append("Consider empirical PPI therapy while awaiting results.")
        elif risk_level == "moderate":
            recommendations.append("Moderate suspicion of gastric disease.")
            recommendations.append("Perform recommended laboratory tests before treatment.")
            recommendations.append("Provide lifestyle and dietary counseling.")
        else:
            recommendations.append("Low risk based on symptoms.")
            recommendations.append("Basic H. pylori screening recommended.")
            recommendations.append("Provide dietary advice and symptom monitoring.")
        
        # Lifestyle recommendations
        if patient_data.get('smoking'):
            recommendations.append("Strongly advise smoking cessation.")
        if patient_data.get('nsaid_use'):
            recommendations.append("Evaluate NSAID use; consider alternatives.")
        
        return recommendations
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train the symptom assessment model."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted'),
            "auc_roc": roc_auc_score(y_test, y_pred_proba),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
        return metrics
    
    def save_model(self):
        """Save the model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, self.model_path)
    
    def load_model(self):
        """Load the model from disk."""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data.get('feature_names', self.feature_names)


class EnhancedLabScreeningModel:
    """
    Stage 2: Enhanced Laboratory-Based Screening Model
    Uses antibody, serology, and other lab tests to determine H. pylori infection
    """
    
    def __init__(self, model_path="models/screening_hp_pos_calibrated.joblib"):
        """Initialize the lab screening model."""
        self.model = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """Load existing screening model."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
    
    def screen(self, lab_data: Dict) -> Dict:
        """
        Perform lab-based screening for H. pylori.
        
        Args:
            lab_data: Dict containing lab test results
            
        Returns:
            Dict with infection probability and recommendations
        """
        # Prepare features based on available lab tests
        features = self._prepare_lab_features(lab_data)
        
        if self.model is not None and len(features) > 0:
            # Use ML model
            features_array = np.array(features).reshape(1, -1)
            prob = self.model.predict_proba(features_array)[0][1]
        else:
            # Rule-based fallback
            prob = self._rule_based_screening(lab_data)
        
        # Determine infection status
        if prob >= 0.7:
            status = "positive"
            confidence = "high"
        elif prob >= 0.4:
            status = "indeterminate"
            confidence = "moderate"
        else:
            status = "negative"
            confidence = "high"
        
        recommendations = self._generate_lab_recommendations(status, prob, lab_data)
        
        return {
            "infection_probability": float(prob),
            "status": status,
            "confidence": confidence,
            "recommendations": recommendations,
            "proceed_to_stage3": status == "positive" or (status == "indeterminate" and prob > 0.5)
        }
    
    def _prepare_lab_features(self, lab_data: Dict) -> List:
        """Convert lab data to features."""
        features = []
        
        # Stool antigen
        if 'stool_antigen' in lab_data:
            features.append(1 if lab_data['stool_antigen'] == 'positive' else 0)
        
        # Serology
        if 'hp_igg' in lab_data:
            features.append(1 if lab_data['hp_igg'] == 'positive' else 0)
        
        # Other markers
        features.append(lab_data.get('hemoglobin', 13))  # Default normal
        features.append(lab_data.get('crp', 1))  # C-reactive protein
        features.append(lab_data.get('wbc', 7))  # White blood cell count
        
        return features
    
    def _rule_based_screening(self, lab_data: Dict) -> float:
        """Rule-based screening logic."""
        score = 0
        
        # Stool antigen - most reliable
        if lab_data.get('stool_antigen') == 'positive':
            score += 0.6
        
        # Serology
        if lab_data.get('hp_igg') == 'positive':
            score += 0.3
        
        # Supporting markers
        if lab_data.get('hemoglobin', 13) < 12:  # Anemia
            score += 0.05
        if lab_data.get('crp', 1) > 5:  # Inflammation
            score += 0.05
        
        return min(score, 1.0)
    
    def _generate_lab_recommendations(self, status: str, prob: float, lab_data: Dict) -> List[str]:
        """Generate recommendations based on lab results."""
        recommendations = []
        
        if status == "positive":
            recommendations.append("H. pylori infection confirmed.")
            recommendations.append("Proceed to Stage 3: Disease staging and treatment planning.")
            recommendations.append("Eradication therapy recommended.")
        elif status == "indeterminate":
            recommendations.append("Inconclusive results - additional testing may be needed.")
            if prob > 0.5:
                recommendations.append("Consider endoscopy with biopsy for definitive diagnosis.")
                recommendations.append("May proceed with empirical treatment if clinical suspicion is high.")
            else:
                recommendations.append("Repeat testing in 2-4 weeks if symptoms persist.")
        else:
            recommendations.append("H. pylori infection not detected.")
            recommendations.append("Consider alternative diagnoses for symptoms.")
            recommendations.append("Provide supportive care and symptom management.")
        
        return recommendations


class RICStagingModel:
    """
    Stage 3: RIC (Risk Index for Chronic gastritis) Staging Model
    Determines disease severity and guides treatment protocols
    """
    
    def __init__(self, model_path="models/staging_3class.joblib"):
        """Initialize the RIC staging model."""
        self.model = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """Load existing staging model."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
    
    def stage_disease(self, ric_data: Dict) -> Dict:
        """
        Determine disease stage based on RIC values.
        
        Args:
            ric_data: Dict containing RIC measurements and clinical data
            
        Returns:
            Dict with stage, severity, and treatment recommendations
        """
        # Prepare features
        features = self._prepare_ric_features(ric_data)
        
        if self.model is not None and len(features) > 0:
            # Use ML model
            features_array = np.array(features).reshape(1, -1)
            stage_probs = self.model.predict_proba(features_array)[0]
            stage = self.model.predict(features_array)[0]
        else:
            # Rule-based fallback
            stage, stage_probs = self._rule_based_staging(ric_data)
        
        # Map stage to severity
        severity_map = {0: "mild", 1: "moderate", 2: "severe"}
        severity = severity_map.get(stage, "moderate")
        
        # Generate treatment protocol
        treatment = self._generate_treatment_protocol(severity, ric_data)
        
        return {
            "stage": severity,
            "stage_confidence": float(max(stage_probs)),
            "stage_probabilities": {
                "mild": float(stage_probs[0]) if len(stage_probs) > 0 else 0,
                "moderate": float(stage_probs[1]) if len(stage_probs) > 1 else 0,
                "severe": float(stage_probs[2]) if len(stage_probs) > 2 else 0
            },
            "treatment_protocol": treatment,
            "biopsy_recommended": severity in ["moderate", "severe"] or ric_data.get('atrophy_present', False)
        }
    
    def _prepare_ric_features(self, ric_data: Dict) -> List:
        """Convert RIC data to features."""
        features = []
        
        # RIC component values
        features.append(ric_data.get('atrophy_score', 0))
        features.append(ric_data.get('intestinal_metaplasia_score', 0))
        features.append(ric_data.get('inflammation_score', 0))
        features.append(ric_data.get('hp_density', 0))
        
        # Clinical markers
        features.append(ric_data.get('pepsinogen_i', 50))
        features.append(ric_data.get('pepsinogen_ii', 10))
        features.append(ric_data.get('gastrin_17', 5))
        
        # Patient factors
        features.append(ric_data.get('age', 40))
        features.append(1 if ric_data.get('sex', '').lower() in ['male', 'm'] else 0)
        
        return features
    
    def _rule_based_staging(self, ric_data: Dict) -> Tuple[int, np.ndarray]:
        """Rule-based staging logic."""
        score = 0
        
        # High-risk factors
        if ric_data.get('atrophy_present'):
            score += 3
        if ric_data.get('intestinal_metaplasia_present'):
            score += 3
        if ric_data.get('hp_density', 0) > 2:
            score += 2
        if ric_data.get('inflammation_score', 0) > 2:
            score += 2
        
        # Biomarkers
        if ric_data.get('pepsinogen_i', 50) < 30:
            score += 1
        if ric_data.get('pepsinogen_ii', 10) > 15:
            score += 1
        if ric_data.get('gastrin_17', 5) < 2 or ric_data.get('gastrin_17', 5) > 15:
            score += 1
        
        # Determine stage
        if score >= 6:
            stage = 2  # Severe
            probs = np.array([0.1, 0.2, 0.7])
        elif score >= 3:
            stage = 1  # Moderate
            probs = np.array([0.2, 0.6, 0.2])
        else:
            stage = 0  # Mild
            probs = np.array([0.7, 0.2, 0.1])
        
        return stage, probs
    
    def _generate_treatment_protocol(self, severity: str, ric_data: Dict) -> Dict:
        """Generate treatment protocol based on severity."""
        protocols = {
            "mild": {
                "regimen": "Standard Triple Therapy",
                "medications": [
                    {"name": "Omeprazole", "dosage": "20mg", "frequency": "twice daily", "duration": "14 days"},
                    {"name": "Clarithromycin", "dosage": "500mg", "frequency": "twice daily", "duration": "14 days"},
                    {"name": "Amoxicillin", "dosage": "1g", "frequency": "twice daily", "duration": "14 days"}
                ],
                "follow_up": "4-6 weeks post-treatment",
                "lifestyle": [
                    "Avoid NSAIDs and aspirin",
                    "Reduce alcohol consumption",
                    "Eat smaller, frequent meals",
                    "Avoid spicy and acidic foods"
                ]
            },
            "moderate": {
                "regimen": "Sequential Therapy or Quadruple Therapy",
                "medications": [
                    {"name": "Esomeprazole", "dosage": "40mg", "frequency": "twice daily", "duration": "14 days"},
                    {"name": "Amoxicillin", "dosage": "1g", "frequency": "twice daily", "duration": "5 days (days 1-5)"},
                    {"name": "Clarithromycin", "dosage": "500mg", "frequency": "twice daily", "duration": "5 days (days 6-10)"},
                    {"name": "Metronidazole", "dosage": "500mg", "frequency": "twice daily", "duration": "5 days (days 6-10)"}
                ],
                "follow_up": "4 weeks post-treatment with confirmatory testing",
                "lifestyle": [
                    "Strict avoidance of NSAIDs",
                    "Avoid alcohol completely",
                    "Smoking cessation mandatory",
                    "Low-fat, bland diet",
                    "Consider endoscopy follow-up"
                ]
            },
            "severe": {
                "regimen": "Bismuth Quadruple Therapy + Extended PPI",
                "medications": [
                    {"name": "Pantoprazole", "dosage": "40mg", "frequency": "twice daily", "duration": "14 days"},
                    {"name": "Bismuth Subsalicylate", "dosage": "300mg", "frequency": "four times daily", "duration": "14 days"},
                    {"name": "Tetracycline", "dosage": "500mg", "frequency": "four times daily", "duration": "14 days"},
                    {"name": "Metronidazole", "dosage": "500mg", "frequency": "three times daily", "duration": "14 days"}
                ],
                "follow_up": "2 weeks during treatment, then 4 weeks post-treatment with endoscopy",
                "lifestyle": [
                    "Complete alcohol and tobacco cessation",
                    "Strict dietary modifications",
                    "Regular monitoring required",
                    "Endoscopic surveillance mandatory",
                    "Consider referral to gastroenterologist"
                ],
                "urgent_notes": "Close monitoring required. Consider hospitalization if bleeding or perforation risk."
            }
        }
        
        protocol = protocols.get(severity, protocols["mild"])
        
        # Add special considerations
        if ric_data.get('atrophy_present') or ric_data.get('intestinal_metaplasia_present'):
            protocol['special_note'] = "⚠️ Pre-cancerous changes detected. Require regular endoscopic surveillance."
        
        return protocol


class ModelRetrainingSystem:
    """System for retraining models as new data accumulates."""
    
    def __init__(self, db_session):
        """Initialize retraining system."""
        self.db = db_session
        self.min_samples_for_retraining = 100  # Minimum new samples needed
    
    def check_retraining_needed(self, model_name: str) -> Dict:
        """Check if a model needs retraining based on accumulated data."""
        from app.models import ModelTraining, Case
        
        # Get current production model
        current_model = self.db.query(ModelTraining).filter(
            ModelTraining.model_name == model_name,
            ModelTraining.is_production == 1
        ).first()
        
        if not current_model:
            return {"retraining_needed": True, "reason": "No production model found"}
        
        # Count new cases since last training
        new_cases = self.db.query(Case).filter(
            Case.created_at > current_model.deployed_at
        ).count()
        
        if new_cases >= self.min_samples_for_retraining:
            return {
                "retraining_needed": True,
                "reason": f"{new_cases} new samples available (threshold: {self.min_samples_for_retraining})",
                "new_samples": new_cases,
                "current_version": current_model.model_version
            }
        
        return {
            "retraining_needed": False,
            "new_samples": new_cases,
            "threshold": self.min_samples_for_retraining
        }
    
    def retrain_model(self, model_name: str, model_obj, X: np.ndarray, y: np.ndarray, user_id: int) -> Dict:
        """
        Retrain a model with accumulated data.
        
        Args:
            model_name: Name of the model
            model_obj: Model object to retrain
            X: Training features
            y: Training labels
            user_id: ID of user initiating retraining
            
        Returns:
            Dict with training results and metrics
        """
        from app.models import ModelTraining
        
        # Create new training record
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        training_record = ModelTraining(
            model_name=model_name,
            model_version=version,
            model_type="classification",
            training_start=datetime.utcnow(),
            status="training",
            dataset_size=len(X),
            trained_by=user_id
        )
        
        self.db.add(training_record)
        self.db.commit()
        
        try:
            # Train model
            metrics = model_obj.train(X, y)
            
            # Save model
            model_obj.save_model()
            
            # Update training record
            training_record.training_end = datetime.utcnow()
            training_record.status = "completed"
            training_record.training_samples = metrics.get("training_samples")
            training_record.test_samples = metrics.get("test_samples")
            training_record.accuracy = metrics.get("accuracy")
            training_record.precision = metrics.get("precision")
            training_record.recall = metrics.get("recall")
            training_record.f1_score = metrics.get("f1_score")
            training_record.auc_roc = metrics.get("auc_roc")
            training_record.model_path = model_obj.model_path
            
            self.db.commit()
            
            return {
                "success": True,
                "version": version,
                "metrics": metrics,
                "training_id": training_record.id
            }
            
        except Exception as e:
            training_record.status = "failed"
            training_record.notes = str(e)
            self.db.commit()
            raise
    
    def deploy_model(self, training_id: int) -> bool:
        """Deploy a trained model to production."""
        from app.models import ModelTraining
        
        training_record = self.db.query(ModelTraining).filter(
            ModelTraining.id == training_id
        ).first()
        
        if not training_record or training_record.status != "completed":
            return False
        
        # Deactivate current production model
        current_production = self.db.query(ModelTraining).filter(
            ModelTraining.model_name == training_record.model_name,
            ModelTraining.is_production == 1
        ).first()
        
        if current_production:
            current_production.is_production = 0
            current_production.replaced_at = datetime.utcnow()
        
        # Activate new model
        training_record.is_production = 1
        training_record.deployed_at = datetime.utcnow()
        
        self.db.commit()
        return True


# Initialize models as singletons
symptom_model = SymptomAssessmentModel()
lab_screening_model = EnhancedLabScreeningModel()
ric_staging_model = RICStagingModel()

