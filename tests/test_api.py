import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app

client = TestClient(app)

def get_test_headers(user_id: str = None):
    """Helper function to create test headers with authorization"""
    if user_id is None:
        user_id = str(uuid4())
    return {"Authorization": f"Bearer {user_id}"}

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to LinkedIn Content Assistant API"}

def test_credits_flow():
    """Test the complete credits flow"""
    # Generate a test user ID
    user_id = str(uuid4())
    headers = get_test_headers(user_id)
    
    # Test credit initialization
    response = client.post("/credits/initialize", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "credits" in data
    assert data["credits"] == 10  # INITIAL_FREE_CREDITS
    
    # Test getting credits
    response = client.get("/credits", headers=headers)
    assert response.status_code == 200
    assert response.json()["credits"] == 10
    
    # Test initializing again (should indicate already initialized)
    response = client.post("/credits/initialize", headers=headers)
    assert response.status_code == 200
    assert "already has credits" in response.json()["message"]

def test_unauthorized_access():
    """Test accessing endpoints without authorization"""
    # Try to get credits without authorization
    response = client.get("/credits", headers={})
    assert response.status_code == 401
    
    # Try to initialize credits without authorization
    response = client.post("/credits/initialize", headers={})
    assert response.status_code == 401 