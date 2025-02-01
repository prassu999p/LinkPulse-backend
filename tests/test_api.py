import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app
from app.models.user import UserProfile, PlanType, NotificationPreferences
from app.models.user_models import Plan
from unittest.mock import patch, AsyncMock
import uuid

# Use the same test UUID as in conftest.py
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"

client = TestClient(app)

@pytest.fixture
def mock_auth():
    """Mock authentication to return a test user"""
    async def mock_get_current_user(*args, **kwargs):
        return {"id": TEST_USER_ID}
    
    with patch('app.middleware.auth.get_current_user', side_effect=mock_get_current_user):
        yield

@pytest.fixture
def auth_headers():
    """Generate test auth headers"""
    return {"Authorization": f"Bearer {TEST_USER_ID}"}

def get_test_headers(user_id: str = None):
    """Helper function to create test headers with authorization"""
    if user_id is None:
        user_id = str(uuid4())
    return {"Authorization": f"Bearer {user_id}"}

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to LinkPulse API"}

def test_credits_flow(mock_auth, auth_headers):
    """Test the complete credits flow"""
    # Test credit initialization
    response = client.post("/credits/initialize", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Test getting credits
    response = client.get("/credits", headers=auth_headers)
    assert response.status_code == 200
    assert "credits" in response.json()
    
    # Test credit deduction
    response = client.post("/credits/deduct", headers=auth_headers, json={"amount": 10})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "remaining_credits" in response.json()

def test_unauthorized_access():
    """Test endpoints without authentication"""
    endpoints = [
        ("POST", "/credits/initialize"),
        ("GET", "/credits"),
        ("POST", "/credits/deduct"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"] 