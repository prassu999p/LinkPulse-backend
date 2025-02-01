import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.credit_service import credit_service
from app.services.email_service import email_service
from app.models.user import UserProfile, Plan, PlanType, NotificationPreferences
from fastapi import HTTPException

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

@pytest.fixture
def mock_email():
    """Mock email service"""
    with patch.object(email_service, '_send_email', new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock

@pytest.fixture
def test_user():
    return UserProfile(
        id="test-user-id",
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

class TestPlanIntegration:
    @pytest.mark.asyncio
    async def test_new_user_initialization(self, mock_db, test_user):
        """Test new user gets correct initial credits"""
        # Act
        success = await credit_service.initialize_user_credits(test_user.id)
        
        # Assert
        assert success is True
        assert mock_db.user_credits[test_user.id] == Plan.get_basic_plan().credits
        assert len(mock_db.credit_history[test_user.id]) == 1
        assert mock_db.credit_history[test_user.id][0]['action_type'] == "INITIAL_ALLOCATION"

    @pytest.mark.asyncio
    async def test_basic_plan_credit_limits(self, mock_db, test_user):
        """Test basic plan users cannot exceed credit limits"""
        # Setup
        await credit_service.initialize_user_credits(test_user.id)
        
        # Try to set credits above basic plan limit
        result = await credit_service.set_user_credits(
            test_user.id, 
            Plan.get_basic_plan().max_credits + 10,
            PlanType.BASIC
        )
        
        # Assert credits are capped at basic plan limit
        assert result is True
        assert mock_db.user_credits[test_user.id] == Plan.get_basic_plan().max_credits

    @pytest.mark.asyncio
    async def test_upgrade_to_pro_flow(self, mock_db, mock_email, test_user):
        """Test complete pro upgrade flow"""
        # Setup initial credits
        await credit_service.initialize_user_credits(test_user.id)
        
        # Send upgrade request
        email_sent = await email_service.send_upgrade_request_to_admin(test_user, "Upgrade request")
        assert email_sent is True
        
        # Confirm upgrade received
        email_sent = await email_service.send_upgrade_request_received(test_user)
        assert email_sent is True
        
        # Process upgrade
        success = await credit_service.upgrade_to_pro(test_user.id)
        assert success is True
        
        # Verify credits updated
        credits = await credit_service.get_user_credits(test_user.id)
        assert credits == Plan.get_pro_plan().credits
        
        # Verify upgrade confirmation email
        test_user.plan_type = PlanType.PRO
        test_user.credits = credits
        email_sent = await email_service.send_upgrade_confirmation(test_user)
        assert email_sent is True

    @pytest.mark.asyncio
    async def test_credit_deduction_basic_plan(self, mock_db, test_user):
        """Test credit deduction for basic plan users"""
        # Setup
        await credit_service.initialize_user_credits(test_user.id)
        initial_credits = await credit_service.get_user_credits(test_user.id)
        
        # Deduct credits
        deduction_amount = 10
        success, remaining = await credit_service.deduct_credits(test_user.id, deduction_amount)
        
        # Assert
        assert success is True
        assert remaining == initial_credits - deduction_amount
        assert mock_db.user_credits[test_user.id] == remaining
        assert len(mock_db.credit_history[test_user.id]) == 2  # Initial + deduction
        assert mock_db.credit_history[test_user.id][-1]['action_type'] == "USAGE"

    @pytest.mark.asyncio
    async def test_credit_deduction_pro_plan(self, mock_db, test_user):
        """Test credit deduction for pro plan users"""
        # Setup pro plan
        await credit_service.upgrade_to_pro(test_user.id)
        initial_credits = await credit_service.get_user_credits(test_user.id)
        
        # Deduct credits
        deduction_amount = 100
        success, remaining = await credit_service.deduct_credits(test_user.id, deduction_amount)
        
        # Assert
        assert success is True
        assert remaining == initial_credits - deduction_amount
        assert mock_db.user_credits[test_user.id] == remaining
        assert mock_db.credit_history[test_user.id][-1]['action_type'] == "USAGE"

    @pytest.mark.asyncio
    async def test_insufficient_credits_handling(self, mock_db, test_user):
        """Test handling of insufficient credits"""
        # Setup basic plan
        await credit_service.initialize_user_credits(test_user.id)
        initial_credits = await credit_service.get_user_credits(test_user.id)
        
        # Try to deduct more than available
        success, remaining = await credit_service.deduct_credits(
            test_user.id, 
            initial_credits + 10
        )
        
        # Assert
        assert success is False
        assert remaining == initial_credits  # Credits should not change
        assert mock_db.user_credits[test_user.id] == initial_credits
        # Should not log failed deduction
        assert mock_db.credit_history[test_user.id][-1]['action_type'] == "INITIAL_ALLOCATION"

    @pytest.mark.asyncio
    async def test_plan_type_determination(self, mock_db, test_user):
        """Test correct plan type determination based on credits"""
        # Setup
        await credit_service.initialize_user_credits(test_user.id)
        
        # Test basic plan
        plan_type = await credit_service.get_user_plan(test_user.id)
        assert plan_type == PlanType.BASIC
        
        # Upgrade to pro
        await credit_service.upgrade_to_pro(test_user.id)
        
        # Test pro plan
        plan_type = await credit_service.get_user_plan(test_user.id)
        assert plan_type == PlanType.PRO 