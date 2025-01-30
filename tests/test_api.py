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

def test_root(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to LinkedIn Content Assistant API"}

def test_credits_flow(test_client, auth_headers):
    """Test the complete credits flow"""
    # Test credit initialization
    response = test_client.post("/credits/initialize", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["credits"] == 10

    # Test getting credits
    response = test_client.get("/credits", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["credits"] == 10

def test_unauthorized_access(test_client):
    """Test accessing endpoints without authorization"""
    # Test without auth header
    response = test_client.get("/credits")
    assert response.status_code == 401

    # Test with invalid auth header
    response = test_client.get("/credits", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401

    # Test credit initialization without auth
    response = test_client.post("/credits/initialize")
    assert response.status_code == 401 