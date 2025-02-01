from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserProfile, PlanType, NotificationPreferences
from app.models.user_models import Plan
from unittest.mock import patch, AsyncMock
import pytest
import uuid

# Use the same test UUID as in conftest.py
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"

client = TestClient(app)

@pytest.fixture(autouse=True)
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

@pytest.fixture
def mock_db():
    """Mock database with test user data"""
    with patch('app.utils.database.get_db') as mock:
        db = AsyncMock()
        db.get_user = AsyncMock(return_value=UserProfile(
            id=TEST_USER_ID,
            email="test@example.com",
            full_name="Test User",
            company="Test Company",
            plan_type=PlanType.BASIC,
            credits=50,
            max_credits=50,
            notification_preferences=NotificationPreferences(),
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        ))
        mock.return_value = db
        yield mock

def test_get_user_profile_unauthorized():
    """Test getting user profile without authentication"""
    with patch('app.middleware.auth.get_current_user', side_effect=None):
        response = client.get("/user/profile")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

def test_get_user_profile(mock_auth, mock_db, auth_headers):
    """Test getting user profile with authentication"""
    response = client.get("/user/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["plan_type"] == PlanType.BASIC.value

def test_update_user_profile(mock_auth, mock_db, auth_headers):
    """Test updating user profile"""
    update_data = {
        "full_name": "Updated User",
        "company": "Updated Company",
        "job_title": "Software Engineer",
        "linkedin_profile": "https://linkedin.com/in/testuser",
        "preferred_tone": "professional",
        "notification_preferences": {
            "email_notifications": True,
            "credit_alerts": True
        }
    }
    
    mock_db.return_value.update_user_profile = AsyncMock(return_value=UserProfile(
        id=TEST_USER_ID,
        email="test@example.com",
        full_name=update_data["full_name"],
        company=update_data["company"],
        job_title=update_data["job_title"],
        linkedin_profile=update_data["linkedin_profile"],
        preferred_tone=update_data["preferred_tone"],
        plan_type=PlanType.BASIC,
        credits=50,
        max_credits=50,
        notification_preferences=NotificationPreferences(**update_data["notification_preferences"]),
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    ))
    
    response = client.put("/user/profile", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["company"] == update_data["company"]
    assert data["job_title"] == update_data["job_title"]

def test_get_user_stats(mock_auth, mock_db, auth_headers):
    """Test getting user statistics"""
    mock_db.return_value.get_user_stats = AsyncMock(return_value=UserStats(
        total_posts_generated=5,
        total_credits_used=25,
        remaining_credits=25,
        last_login="2024-01-01T00:00:00",
        account_created="2024-01-01T00:00:00"
    ))
    
    response = client.get("/user/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_posts_generated"] == 5
    assert data["total_credits_used"] == 25
    assert data["remaining_credits"] == 25

def test_update_notification_preferences(mock_auth, mock_db, auth_headers):
    """Test updating notification preferences"""
    preferences = {
        "email_notifications": False,
        "credit_alerts": True
    }
    
    mock_db.return_value.update_notification_preferences = AsyncMock(return_value=True)
    
    response = client.put("/user/notification-preferences", headers=auth_headers, json=preferences)
    assert response.status_code == 200
    assert response.json()["success"] is True 