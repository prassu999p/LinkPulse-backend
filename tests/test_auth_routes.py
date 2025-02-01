import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.database import Database
from unittest.mock import patch, MagicMock

client = TestClient(app)

class MockSupabaseClient:
    def __init__(self):
        self.auth = MagicMock()
        self.auth.sign_up = MagicMock()
        self.auth.sign_in_with_password = MagicMock()
        self._from = MagicMock()
        self._from.insert = MagicMock()
        self._from.insert.execute = MagicMock()

    def from_(self, *args, **kwargs):
        return self._from

class MockDatabase:
    def __init__(self):
        self.client = MockSupabaseClient()
        self.settings = MagicMock()
        self.settings.INITIAL_FREE_CREDITS = 10
        self.get_user_by_email = MagicMock()

@pytest.fixture
def mock_db():
    with patch('app.routes.auth_routes.get_db') as mock:
        db = MockDatabase()
        mock.return_value = db
        yield db

def test_register_success(mock_db):
    # Mock Supabase auth response
    mock_db.client.auth.sign_up.return_value = MagicMock(
        user=MagicMock(id="test-user-id"),
        session=MagicMock(access_token="test-token")
    )
    
    # Mock database insert
    mock_db.client._from.insert.execute.return_value = MagicMock(data=[{"id": "test-user-id"}])
    
    # Mock get_user_by_email to return None (user doesn't exist)
    mock_db.get_user_by_email.return_value = None

    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "company": "Test Company",
            "job_title": "Test Role"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["credits"] == 10

def test_register_existing_user(mock_db):
    # Mock get_user_by_email to return existing user
    mock_db.get_user_by_email.return_value = {"id": "existing-user"}

    response = client.post(
        "/auth/register",
        json={
            "email": "existing@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(mock_db):
    # Mock Supabase auth response
    mock_db.client.auth.sign_in_with_password.return_value = MagicMock(
        user=MagicMock(id="test-user-id"),
        session=MagicMock(access_token="test-token")
    )
    
    # Mock get_user_by_email
    mock_db.get_user_by_email.return_value = {
        "id": "test-user-id",
        "email": "test@example.com",
        "credits": 10
    }

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["credits"] == 10

def test_login_invalid_credentials(mock_db):
    # Mock auth failure
    mock_db.client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_create_user_credits(mock_db):
    # Mock Supabase auth response with new user
    mock_db.client.auth.sign_in_with_password.return_value = MagicMock(
        user=MagicMock(id="new-user-id"),
        session=MagicMock(access_token="test-token")
    )
    
    # Mock user not found in database
    mock_db.get_user_by_email.return_value = None
    
    # Mock successful credits creation
    mock_db.client._from.insert.execute.return_value = MagicMock(data=[{"id": "new-user-id"}])

    response = client.post(
        "/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["credits"] == 10

def test_register_validation(mock_db):
    # Test invalid email format
    response = client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 422

    # Test missing required fields
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422

def test_login_validation(mock_db):
    # Test invalid email format
    response = client.post(
        "/auth/login",
        json={
            "email": "invalid-email",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 422

    # Test missing required fields
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422 