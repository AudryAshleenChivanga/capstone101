"""Tests for multi-stage clinical workflow endpoints."""
import pytest
from fastapi import status


def test_stage1_symptom_assessment(client, auth_headers):
    """Test Stage 1: Symptom Assessment."""
    response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "John Doe",
            "age": 45,
            "sex": "M",
            "residence": "urban",
            "abdominal_pain": 1,
            "nausea": 1,
            "bloating": 1,
            "weight_loss": 0,
            "vomiting_blood": 0
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "patient_id" in data
    assert "case_id" in data
    assert "assessment" in data
    assert data["assessment"]["risk_level"] in ['low', 'moderate', 'high']
    assert "recommendations" in data["assessment"]


def test_stage1_requires_auth(client):
    """Test that Stage 1 requires authentication."""
    response = client.post("/workflow/stage1/symptom-assessment",
        json={
            "patient_name": "John Doe",
            "age": 45
        })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_stage2_lab_screening(client, auth_headers):
    """Test Stage 2: Lab Screening."""
    # First create a Stage 1 case
    stage1_response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Jane Smith",
            "age": 50,
            "sex": "F",
            "residence": "urban",
            "abdominal_pain": 1
        })
    
    stage1_data = stage1_response.json()
    patient_id = stage1_data["patient_id"]
    case_id = stage1_data["case_id"]
    
    # Now perform Stage 2
    response = client.post("/workflow/stage2/lab-screening",
        headers=auth_headers,
        json={
            "patient_id": patient_id,
            "case_id": case_id,
            "stool_antigen": "positive",
            "hp_igg": "positive",
            "hemoglobin": 12.5,
            "crp": 8.5,
            "wbc": 9.0,
            "esr": 15,
            "platelet_count": 250
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "screening_result" in data
    assert "probability" in data["screening_result"]
    assert "risk_level" in data["screening_result"]
    assert 0 <= data["screening_result"]["probability"] <= 1


def test_stage3_ric_staging(client, auth_headers):
    """Test Stage 3: Antibiotic Resistance Staging."""
    # Create Stage 1 and 2 first
    stage1_response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Bob Johnson",
            "age": 55,
            "sex": "M",
            "abdominal_pain": 1
        })
    
    stage1_data = stage1_response.json()
    patient_id = stage1_data["patient_id"]
    stage1_case_id = stage1_data["case_id"]
    
    stage2_response = client.post("/workflow/stage2/lab-screening",
        headers=auth_headers,
        json={
            "patient_id": patient_id,
            "case_id": stage1_case_id,
            "stool_antigen": "positive",
            "hp_igg": "positive",
            "hemoglobin": 12.0,
            "crp": 10.0,
            "wbc": 8.5
        })
    
    stage2_data = stage2_response.json()
    stage2_case_id = stage2_data["case_id"]
    
    # Now perform Stage 3
    response = client.post("/workflow/stage3/ric-staging",
        headers=auth_headers,
        json={
            "patient_id": patient_id,
            "case_id": stage2_case_id,
            "mic_clarithromycin": 2.5,
            "mic_metronidazole": 8.0,
            "mic_levofloxacin": 1.5,
            "mutation_a2143g": 1,
            "mutation_a2144g": 0,
            "mutation_rdxa": 0,
            "mutation_gyra": 0
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "staging_result" in data
    assert "stage" in data["staging_result"]
    assert data["staging_result"]["stage"] in ['low', 'moderate', 'high']
    assert "treatment_protocol" in data["staging_result"]


def test_patient_journey(client, auth_headers):
    """Test retrieving complete patient journey."""
    # Create a patient with some cases
    stage1_response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Alice Cooper",
            "age": 42,
            "sex": "F",
            "abdominal_pain": 1
        })
    
    patient_id = stage1_response.json()["patient_id"]
    
    # Get patient journey
    response = client.get(f"/workflow/patient-journey/{patient_id}",
        headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "patient_id" in data
    assert "patient_name" in data
    assert "cases" in data
    assert isinstance(data["cases"], list)


def test_complete_workflow_integration(client, auth_headers):
    """Test complete workflow from symptoms to treatment recommendation."""
    # Stage 1: Symptom Assessment
    stage1_response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Integration Test Patient",
            "age": 48,
            "sex": "M",
            "residence": "urban",
            "abdominal_pain": 1,
            "nausea": 1,
            "weight_loss": 1,
            "smoking": 1,
            "nsaid_use": 1
        })
    
    assert stage1_response.status_code == 200
    stage1_data = stage1_response.json()
    patient_id = stage1_data["patient_id"]
    stage1_case_id = stage1_data["case_id"]
    
    # Stage 2: Lab Screening
    stage2_response = client.post("/workflow/stage2/lab-screening",
        headers=auth_headers,
        json={
            "patient_id": patient_id,
            "case_id": stage1_case_id,
            "stool_antigen": "positive",
            "hp_igg": "positive",
            "hemoglobin": 11.5,
            "crp": 15.0,
            "wbc": 10.5,
            "esr": 20,
            "platelet_count": 280
        })
    
    assert stage2_response.status_code == 200
    stage2_data = stage2_response.json()
    stage2_case_id = stage2_data["case_id"]
    
    # Check if screening is positive (probability > 0.5)
    if stage2_data["screening_result"]["probability"] > 0.5:
        # Stage 3: RIC Staging
        stage3_response = client.post("/workflow/stage3/ric-staging",
            headers=auth_headers,
            json={
                "patient_id": patient_id,
                "case_id": stage2_case_id,
                "mic_clarithromycin": 3.0,
                "mic_metronidazole": 10.0,
                "mic_levofloxacin": 2.0,
                "mutation_a2143g": 1,
                "mutation_a2144g": 1,
                "mutation_rdxa": 0,
                "mutation_gyra": 0
            })
        
        assert stage3_response.status_code == 200
        stage3_data = stage3_response.json()
        
        # Verify treatment protocol is provided
        assert "treatment_protocol" in stage3_data["staging_result"]
        protocol = stage3_data["staging_result"]["treatment_protocol"]
        assert "medications" in protocol
        assert len(protocol["medications"]) > 0


def test_invalid_patient_id(client, auth_headers):
    """Test that invalid patient ID returns appropriate error."""
    response = client.post("/workflow/stage2/lab-screening",
        headers=auth_headers,
        json={
            "patient_id": "INVALID-ID",
            "case_id": 99999,
            "stool_antigen": "positive",
            "hp_igg": "positive",
            "hemoglobin": 12.0
        })
    
    assert response.status_code in [404, 422]


def test_missing_required_fields(client, auth_headers):
    """Test that missing required fields returns validation error."""
    response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Test"
            # Missing age and sex
        })
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

