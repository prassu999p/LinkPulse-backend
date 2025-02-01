import pytest
from fastapi import HTTPException
from app.services.credit_service import credit_service
from app.models.user import Plan, PlanType
from app.utils.database import get_db
from unittest.mock import AsyncMock, patch, MagicMock

pytestmark = pytest.mark.asyncio

class MockDB:
    def __init__(self):
        self.user_credits = {}
        self.credit_history = {}
        
    async def get_user_credits(self, user_id: str):
        return self.user_credits.get(user_id, None)
    
    async def set_user_credits(self, user_id: str, credits: int):
        self.user_credits[user_id] = credits
        return True
    
    async def log_credit_transaction(self, user_id: str, amount: int, action_type: str, description: str = None):
        if user_id not in self.credit_history:
            self.credit_history[user_id] = []
        self.credit_history[user_id].append({
            'amount': amount,
            'action_type': action_type,
            'description': description
        })
        return True

@pytest.fixture
async def mock_db():
    """Mock database with state tracking"""
    mock_db = MockDB()
    
    # Create async mock methods
    mock_db.get_user_credits = AsyncMock(side_effect=mock_db.get_user_credits)
    mock_db.set_user_credits = AsyncMock(side_effect=mock_db.set_user_credits)
    mock_db.log_credit_transaction = AsyncMock(side_effect=mock_db.log_credit_transaction)
    
    # Mock the get_db function
    with patch('app.services.credit_service.get_db', return_value=mock_db):
        yield mock_db

@pytest.mark.asyncio
async def test_initialize_user_credits(mock_db):
    """Test initializing credits for new user"""
    # Arrange
    user_id = "test-user-id"
    
    # Act
    result = await credit_service.initialize_user_credits(user_id)
    
    # Assert
    assert result is True
    assert mock_db.user_credits[user_id] == Plan.get_basic_plan().credits
    assert len(mock_db.credit_history[user_id]) == 1
    assert mock_db.credit_history[user_id][0]['action_type'] == "INITIAL_ALLOCATION"

@pytest.mark.asyncio
async def test_get_user_credits(mock_db):
    """Test getting user credits"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 50
    
    # Act
    credits = await credit_service.get_user_credits(user_id)
    
    # Assert
    assert credits == 50
    mock_db.get_user_credits.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_set_user_credits_basic_plan(mock_db):
    """Test setting credits for basic plan user"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 30
    
    # Act
    result = await credit_service.set_user_credits(user_id, 60, PlanType.BASIC)
    
    # Assert
    assert result is True
    # Should be limited to basic plan max credits (50)
    assert mock_db.user_credits[user_id] == Plan.get_basic_plan().max_credits

@pytest.mark.asyncio
async def test_set_user_credits_pro_plan(mock_db):
    """Test setting credits for pro plan user"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 100
    
    # Act
    result = await credit_service.set_user_credits(user_id, 400, PlanType.PRO)
    
    # Assert
    assert result is True
    assert mock_db.user_credits[user_id] == 400

@pytest.mark.asyncio
async def test_upgrade_to_pro(mock_db):
    """Test upgrading user to pro plan"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 50
    
    # Act
    result = await credit_service.upgrade_to_pro(user_id)
    
    # Assert
    assert result is True
    assert mock_db.user_credits[user_id] == Plan.get_pro_plan().credits
    assert len(mock_db.credit_history[user_id]) > 0
    assert mock_db.credit_history[user_id][-1]['action_type'] == "PLAN_UPGRADE"

@pytest.mark.asyncio
async def test_deduct_credits(mock_db):
    """Test credit deduction"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 50
    
    # Act
    success, remaining = await credit_service.deduct_credits(user_id, 20)
    
    # Assert
    assert success is True
    assert remaining == 30
    assert mock_db.user_credits[user_id] == 30
    assert len(mock_db.credit_history[user_id]) > 0
    assert mock_db.credit_history[user_id][-1]['action_type'] == "USAGE"

@pytest.mark.asyncio
async def test_insufficient_credits(mock_db):
    """Test deduction with insufficient credits"""
    # Arrange
    user_id = "test-user-id"
    mock_db.user_credits[user_id] = 10
    initial_history_count = len(mock_db.credit_history.get(user_id, []))
    
    # Act
    success, remaining = await credit_service.deduct_credits(user_id, 20)
    
    # Assert
    assert success is False
    assert remaining == 10
    assert mock_db.user_credits[user_id] == 10  # Credits should not change
    assert len(mock_db.credit_history.get(user_id, [])) == initial_history_count  # No transaction logged

@pytest.mark.asyncio
async def test_get_user_plan(mock_db):
    """Test getting user plan type"""
    # Arrange
    user_id = "test-user-id"
    
    # Test Basic Plan
    mock_db.user_credits[user_id] = 50
    basic_plan = await credit_service.get_user_plan(user_id)
    assert basic_plan == PlanType.BASIC
    
    # Test Pro Plan
    mock_db.user_credits[user_id] = 100
    pro_plan = await credit_service.get_user_plan(user_id)
    assert pro_plan == PlanType.PRO

@pytest.mark.asyncio
async def test_get_nonexistent_user(mock_db):
    """Test getting credits for nonexistent user"""
    with pytest.raises(HTTPException) as exc_info:
        await credit_service.get_user_credits("nonexistent-user")
    assert exc_info.value.status_code == 404
    assert "User credits not found" in str(exc_info.value.detail) 