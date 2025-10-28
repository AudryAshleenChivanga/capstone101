"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.db import Base, get_db
from app.models import User
from app.auth import hash_password

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    """Create a test user."""
    db = TestingSessionLocal()
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        role="clinician"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    
    return user


@pytest.fixture
def test_admin(client):
    """Create a test admin user."""
    db = TestingSessionLocal()
    
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin"
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Get authentication headers for admin user."""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "adminpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
