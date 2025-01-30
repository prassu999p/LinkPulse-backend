import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import verify_token
from app.utils.database import db
from uuid import UUID
from fastapi import HTTPException

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Mock database operations for testing"""
    test_users = {}
    test_transactions = []

    async def mock_get_user(user_id: str):
        return test_users.get(user_id)

    async def mock_create_user(user_id: str, auth_provider: str = 'email'):
        test_users[user_id] = {
            "user_id": user_id,
            "credits_remaining": 10,  # Initial free credits
            "auth_provider": auth_provider
        }
        return test_users[user_id]

    async def mock_update_user_credits(user_id: str, credits: int):
        if user_id in test_users:
            test_users[user_id]["credits_remaining"] = credits
            return True
        return False

    async def mock_log_transaction(user_id: str, credit_change: int, action_type: str):
        if user_id in test_users:
            test_transactions.append({
                "user_id": user_id,
                "credit_change": credit_change,
                "action_type": action_type
            })
            return test_transactions[-1]
        return None

    monkeypatch.setattr(db, "get_user", mock_get_user)
    monkeypatch.setattr(db, "create_user", mock_create_user)
    monkeypatch.setattr(db, "update_user_credits", mock_update_user_credits)
    monkeypatch.setattr(db, "log_transaction", mock_log_transaction)

@pytest.fixture
def test_client():
    """Create a test client with mocked authentication"""
    async def mock_verify_token(credentials):
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Missing authentication token"
            )
        
        try:
            user_id = credentials.credentials
            uuid.UUID(user_id)  # Validate UUID format
            return user_id
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token format"
            )

    app.dependency_overrides[verify_token] = mock_verify_token
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_id():
    return "123e4567-e89b-12d3-a456-426614174000"

@pytest.fixture
def auth_headers(test_user_id):
    return {"Authorization": f"Bearer {test_user_id}"} 