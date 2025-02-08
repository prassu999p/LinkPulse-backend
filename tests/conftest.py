import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import verify_token
from app.utils.database import get_db
import uuid
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from app.models.user import UserProfile, NotificationPreferences, PlanType
from app.models.user_models import Plan

# Create a constant test UUID
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"

@pytest.fixture(autouse=True)
async def mock_db(monkeypatch):
    """Mock database operations for testing"""
    test_users = {}
    test_transactions = []

    async def mock_get_user(user_id: str):
        user_id = user_id.get('id') if isinstance(user_id, dict) else user_id
        if user_id not in test_users:
            test_users[user_id] = UserProfile(
                id=user_id,
                email="test@example.com",
                full_name=None,
                company=None,
                job_title=None,
                linkedin_profile=None,
                preferred_tone=None,
                notification_preferences=NotificationPreferences(),
                plan_type=PlanType.BASIC,
                credits=50,
                max_credits=50,
                created_at="2024-01-30T00:00:00Z",
                updated_at="2024-01-30T00:00:00Z"
            )
        return test_users[user_id]

    async def mock_update_user_profile(user_id: str, profile_data: dict):
        user_id = user_id.get('id') if isinstance(user_id, dict) else user_id
        if user_id in test_users:
            user = test_users[user_id]
            for key, value in profile_data.items():
                setattr(user, key, value)
            return user
        return None

    async def mock_get_user_stats(user_id: str):
        user_id = user_id.get('id') if isinstance(user_id, dict) else user_id
        return UserStats(
            total_posts_generated=5,
            total_credits_used=25,
            remaining_credits=25,
            last_login="2024-01-30T00:00:00Z",
            account_created="2024-01-30T00:00:00Z"
        )

    async def mock_update_notification_preferences(user_id: str, preferences: dict):
        user_id = user_id.get('id') if isinstance(user_id, dict) else user_id
        if user_id in test_users:
            test_users[user_id].notification_preferences = NotificationPreferences(**preferences)
            return True
        return False

    class MockDB:
        async def get_user(self, user_id):
            return await mock_get_user(user_id)
            
        async def update_user_profile(self, user_id, profile_data):
            return await mock_update_user_profile(user_id, profile_data)
            
        async def get_user_stats(self, user_id):
            return await mock_get_user_stats(user_id)
            
        async def update_notification_preferences(self, user_id, preferences):
            return await mock_update_notification_preferences(user_id, preferences)

    async def mock_get_db():
        return MockDB()

    monkeypatch.setattr("app.utils.database.get_db", mock_get_db)

@pytest.fixture
def test_client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def test_user_id():
    """Generate a test user ID"""
    return str(uuid.uuid4())

@pytest.fixture
def auth_headers():
    """Return authentication headers for testing"""
    return {"Authorization": f"Bearer {TEST_USER_ID}"}

@pytest.fixture
def mock_auth():
    """Mock authentication to return a test user"""
    async def mock_get_current_user(*args, **kwargs):
        return {"id": TEST_USER_ID}
    
    with patch('app.middleware.auth.get_current_user', side_effect=mock_get_current_user):
        yield

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

@pytest.fixture
def test_user():
    """Return a test user profile"""
    return UserProfile(
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
    ) 