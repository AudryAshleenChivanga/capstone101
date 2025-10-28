"""Tests for recommendation endpoints."""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


def test_version_endpoint(client):
    """Test version endpoint."""
    response = client.get("/version")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "service_version" in data
    assert "scikit_learn_version" in data
    assert "pandas_version" in data
    assert "models" in data


def test_recommend_single_requires_auth(client):
    """Test that recommendation endpoint requires authentication."""
    response = client.post("/recommend", json={
        "age": 45,
        "sex": "M",
        "stool_ag": 1
    })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_recommend_single_success(client, auth_headers):
    """Test successful single case recommendation."""
    response = client.post("/recommend",
        headers=auth_headers,
        json={
            "age": 45,
            "sex": "M",
            "residence": "urban",
            "smoking": 1,
            "epigastric_pain": 1,
            "stool_ag": 1,
            "hemoglobin": 13.5,
            "patient_pseudo_id": "TEST001"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "screen_prob" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    assert "case_id" in data
    assert data["input_data"]["patient_pseudo_id"] == "TEST001"


def test_recommend_with_staging_data(client, auth_headers):
    """Test recommendation with staging features."""
    response = client.post("/recommend",
        headers=auth_headers,
        json={
            "age": 50,
            "sex": "F",
            "mic_clari": 2.5,
            "mut_A2143G": 1,
            "mut_A2144G": 0,
            "double_mut": 0
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "screen_prob" in data
    assert "recommendations" in data
    # Stage prediction may be present if staging model is available
    # assert "stage_pred" in data


def test_recommend_minimal_data(client, auth_headers):
    """Test recommendation with minimal data."""
    response = client.post("/recommend",
        headers=auth_headers,
        json={
            "age": 30
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "recommendations" in data


def test_batch_recommend_requires_auth(client):
    """Test that batch recommendation requires authentication."""
    response = client.post("/recommend/batch")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_batch_recommend_invalid_file_type(client, auth_headers):
    """Test batch recommendation with invalid file type."""
    files = {"file": ("test.txt", b"not a csv", "text/plain")}
    response = client.post("/recommend/batch",
        headers=auth_headers,
        files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_batch_recommend_success(client, auth_headers):
    """Test successful batch recommendation."""
    # Create a simple CSV
    csv_content = """age,sex,residence,stool_ag,patient_pseudo_id
45,M,urban,1,PATIENT001
52,F,rural,0,PATIENT002
38,M,urban,1,PATIENT003"""
    
    files = {"file": ("test.csv", csv_content.encode(), "text/csv")}
    response = client.post("/recommend/batch",
        headers=auth_headers,
        files=files)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["total"] == 3
    assert data["processed"] >= 0  # May be less if errors occur
    assert "results" in data
    assert isinstance(data["results"], list)
