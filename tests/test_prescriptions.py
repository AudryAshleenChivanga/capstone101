"""Tests for prescription management endpoints."""
import pytest
from fastapi import status


@pytest.fixture
def sample_prescription_data(client, auth_headers):
    """Create a workflow case to base prescription on."""
    # Create Stage 1
    stage1_response = client.post("/workflow/stage1/symptom-assessment",
        headers=auth_headers,
        json={
            "patient_name": "Prescription Test Patient",
            "age": 50,
            "sex": "M",
            "abdominal_pain": 1
        })
    
    stage1_data = stage1_response.json()
    return {
        "patient_id": stage1_data["patient_id"],
        "case_id": stage1_data["case_id"]
    }


def test_create_prescription(client, auth_headers, sample_prescription_data):
    """Test creating a prescription."""
    response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori infection - moderate resistance",
            "medications": [
                {
                    "name": "Omeprazole",
                    "dosage": "20mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                },
                {
                    "name": "Amoxicillin",
                    "dosage": "1000mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                },
                {
                    "name": "Clarithromycin",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                }
            ],
            "recommendations": "Complete full course. Take with meals.",
            "lifestyle_advice": "Avoid alcohol, quit smoking",
            "follow_up_days": 28,
            "stage": "stage3_ric",
            "protocol_type": "eradication"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "prescription_id" in data
    assert data["patient_id"] == sample_prescription_data["patient_id"]


def test_create_prescription_requires_auth(client, sample_prescription_data):
    """Test that creating prescription requires authentication."""
    response = client.post("/prescriptions/",
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "Test diagnosis",
            "medications": []
        })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_prescription(client, auth_headers, sample_prescription_data):
    """Test retrieving a prescription."""
    # First create a prescription
    create_response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori infection",
            "medications": [
                {
                    "name": "Omeprazole",
                    "dosage": "20mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                }
            ],
            "recommendations": "Complete course",
            "follow_up_days": 28
        })
    
    prescription_id = create_response.json()["prescription_id"]
    
    # Now retrieve it
    response = client.get(f"/prescriptions/{prescription_id}",
        headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == prescription_id
    assert data["diagnosis"] == "H. pylori infection"
    assert len(data["medications"]) > 0


def test_get_patient_prescriptions(client, auth_headers, sample_prescription_data):
    """Test getting all prescriptions for a patient."""
    # Create a prescription
    client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori",
            "medications": [{"name": "Omeprazole", "dosage": "20mg", "frequency": "Daily", "duration": "14 days"}]
        })
    
    # Get patient prescriptions
    response = client.get(f"/prescriptions/patient/{sample_prescription_data['patient_id']}",
        headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "prescriptions" in data
    assert "total" in data
    assert data["total"] >= 1


def test_update_prescription(client, auth_headers, sample_prescription_data):
    """Test updating a prescription."""
    # Create prescription
    create_response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "Initial diagnosis",
            "medications": [{"name": "Drug1", "dosage": "10mg", "frequency": "Daily", "duration": "7 days"}],
            "status": "pending"
        })
    
    prescription_id = create_response.json()["prescription_id"]
    
    # Update it
    response = client.put(f"/prescriptions/{prescription_id}",
        headers=auth_headers,
        json={
            "status": "dispensed",
            "notes": "Patient picked up medication"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert data["prescription_id"] == prescription_id


def test_get_case_prescription(client, auth_headers, sample_prescription_data):
    """Test getting prescription associated with a case."""
    # Create prescription
    client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori",
            "medications": [{"name": "Test Drug", "dosage": "10mg", "frequency": "Daily", "duration": "14 days"}]
        })
    
    # Get prescription by case
    response = client.get(f"/prescriptions/case/{sample_prescription_data['case_id']}",
        headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["has_prescription"] is True
    assert "prescription" in data


def test_prescription_print_view(client, auth_headers, sample_prescription_data):
    """Test prescription print view."""
    # Create prescription
    create_response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori infection",
            "medications": [
                {
                    "name": "Omeprazole",
                    "dosage": "20mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                }
            ]
        })
    
    prescription_id = create_response.json()["prescription_id"]
    
    # Get print view
    response = client.get(f"/prescriptions/{prescription_id}/print",
        headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "print_data" in data
    assert "patient" in data["print_data"]
    assert "medications" in data["print_data"]


def test_prescription_with_invalid_patient(client, auth_headers):
    """Test creating prescription with invalid patient ID."""
    response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": "INVALID-ID",
            "case_id": 99999,
            "diagnosis": "Test",
            "medications": []
        })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_prescription_medication_validation(client, auth_headers, sample_prescription_data):
    """Test that prescriptions with proper medications are created."""
    response = client.post("/prescriptions/",
        headers=auth_headers,
        json={
            "patient_id": sample_prescription_data["patient_id"],
            "case_id": sample_prescription_data["case_id"],
            "diagnosis": "H. pylori - low resistance",
            "medications": [
                {
                    "name": "Proton Pump Inhibitor",
                    "dosage": "20mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                },
                {
                    "name": "Amoxicillin",
                    "dosage": "1000mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                },
                {
                    "name": "Clarithromycin",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "duration": "14 days"
                }
            ],
            "protocol_type": "eradication"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify prescription was created with medications
    prescription_id = data["prescription_id"]
    get_response = client.get(f"/prescriptions/{prescription_id}",
        headers=auth_headers)
    
    prescription = get_response.json()
    assert len(prescription["medications"]) == 3
    assert prescription["protocol_type"] == "eradication"

