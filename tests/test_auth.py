"""Tests for authentication endpoints."""
import pytest
from fastapi import status


def test_register_first_user(client):
    """Test registering the first admin user."""
    response = client.post("/auth/register/first", json={
        "username": "firstadmin",
        "email": "admin@test.com",
        "password": "securepass123",
        "role": "admin"
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "firstadmin"
    assert data["role"] == "admin"
    assert "hashed_password" not in data


def test_register_first_user_fails_if_users_exist(client, test_user):
    """Test that first user registration fails if users already exist."""
    response = client.post("/auth/register/first", json={
        "username": "anotheruser",
        "email": "another@test.com",
        "password": "password123",
        "role": "admin"
    })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_register_user_admin_only(client, admin_headers):
    """Test that regular user registration requires admin role."""
    response = client.post("/auth/register", 
        headers=admin_headers,
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
            "role": "clinician"
        })
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "clinician"


def test_register_user_without_admin_fails(client, auth_headers):
    """Test that non-admin users cannot register new users."""
    response = client.post("/auth/register",
        headers=auth_headers,
        json={
            "username": "unauthorized",
            "email": "unauth@test.com",
            "password": "password123",
            "role": "clinician"
        })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_register_duplicate_username(client, admin_headers, test_user):
    """Test that registering duplicate username fails."""
    response = client.post("/auth/register",
        headers=admin_headers,
        json={
            "username": "testuser",  # Already exists
            "email": "newemail@test.com",
            "password": "password123",
            "role": "clinician"
        })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"


def test_login_invalid_username(client):
    """Test login with invalid username."""
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_invalid_password(client, test_user):
    """Test login with invalid password."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "clinician"


def test_get_current_user_without_auth(client):
    """Test that getting current user fails without authentication."""
    response = client.get("/auth/me")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_invalid_token(client):
    """Test request with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
