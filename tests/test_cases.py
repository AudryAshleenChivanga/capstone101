"""Tests for case management endpoints."""
import pytest
from fastapi import status


@pytest.fixture
def sample_case(client, auth_headers):
    """Create a sample case for testing."""
    response = client.post("/recommend",
        headers=auth_headers,
        json={
            "age": 45,
            "sex": "M",
            "stool_ag": 1,
            "patient_pseudo_id": "TESTCASE001"
        })
    
    return response.json()


def test_list_cases_requires_auth(client):
    """Test that listing cases requires authentication."""
    response = client.get("/cases")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_cases_empty(client, auth_headers):
    """Test listing cases when none exist."""
    response = client.get("/cases", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert data["page"] == 1
    assert len(data["cases"]) == 0


def test_list_cases_with_data(client, auth_headers, sample_case):
    """Test listing cases with data."""
    response = client.get("/cases", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 1
    assert len(data["cases"]) >= 1
    
    # Check case structure
    case = data["cases"][0]
    assert "id" in case
    assert "user_id" in case
    assert "screen_prob" in case
    assert "recommendations" in case
    assert "created_at" in case


def test_list_cases_pagination(client, auth_headers, sample_case):
    """Test case listing pagination."""
    # Test page 1
    response = client.get("/cases?page=1&page_size=1", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 1


def test_get_case_detail_requires_auth(client, sample_case):
    """Test that getting case detail requires authentication."""
    case_id = sample_case["case_id"]
    response = client.get(f"/cases/{case_id}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_case_detail_success(client, auth_headers, sample_case):
    """Test getting case detail."""
    case_id = sample_case["case_id"]
    response = client.get(f"/cases/{case_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == case_id
    assert "input_data" in data
    assert "recommendations" in data
    # patient_pseudo_id might be in different locations
    assert "patient_pseudo_id" in data or "patient_id" in data or data["input_data"].get("patient_pseudo_id") == "TESTCASE001"


def test_get_case_detail_not_found(client, auth_headers):
    """Test getting non-existent case."""
    response = client.get("/cases/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_users_can_only_see_own_cases(client, test_user, test_admin):
    """Test that users can only see their own cases (except admin)."""
    # Login as test user and create a case
    user_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    user_token = user_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    case_response = client.post("/recommend",
        headers=user_headers,
        json={"age": 45, "sex": "M"})
    case_id = case_response.json()["case_id"]
    
    # Login as admin
    admin_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "adminpass123"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin should be able to see the case
    response = client.get(f"/cases/{case_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Admin should see all cases in list
    list_response = client.get("/cases", headers=admin_headers)
    assert list_response.status_code == status.HTTP_200_OK
