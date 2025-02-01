import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import EmailStr

client = TestClient(app)

class MockUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email

class MockSession:
    def __init__(self, access_token):
        self.access_token = access_token

class MockAuthResponse:
    def __init__(self, user, session):
        self.user = user
        self.session = session

class MockSupabaseAuth:
    def __init__(self):
        self.sign_up = MagicMock()
        self.sign_in_with_password = MagicMock()

class MockSupabaseClient:
    def __init__(self):
        self.auth = MockSupabaseAuth()
        self._from = MagicMock()
        self._from.insert = MagicMock(return_value=self._from)
        self._from.execute = MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))

    def from_(self, *args, **kwargs):
        return self._from

@pytest.fixture
def mock_db():
    with patch('app.routes.auth_routes.get_db') as mock:
        db = MagicMock()
        db.client = MockSupabaseClient()
        db.settings = MagicMock()
        db.settings.INITIAL_FREE_CREDITS = 10
        
        # Mock the get_user_by_email method as an async method
        async def mock_get_user_by_email(email):
            return None
        db.get_user_by_email = mock_get_user_by_email
        
        mock.return_value = db
        yield db

def test_register_validation(mock_db):
    # Test invalid email format
    mock_db.client.auth.sign_up.side_effect = Exception("Unable to validate email address: invalid format")
    
    response = client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 500
    assert "Unable to validate email address" in response.json()["detail"]

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
    mock_db.client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
    
    response = client.post(
        "/auth/login",
        json={
            "email": "invalid-email",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    # Test missing required fields
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422

def test_register_success(mock_db):
    # Create mock objects with proper structure
    user = MockUser(id="test-user-id", email="test@example.com")
    session = MockSession(access_token="test-token")
    auth_response = MockAuthResponse(user=user, session=session)
    
    # Set up the mock response
    mock_db.client.auth.sign_up.return_value = auth_response
    
    # Mock the database insert response
    mock_db.client._from.execute.return_value = MagicMock(data=[{"id": "test-user-id"}])
    
    # Mock the get_user_by_email method
    async def mock_get_user_by_email(email):
        return None
    mock_db.get_user_by_email = mock_get_user_by_email

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