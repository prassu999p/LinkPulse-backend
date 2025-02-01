import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.email_service import email_service
from app.models.user import UserProfile, NotificationPreferences, PlanType
from app.models.user_models import Plan
from smtplib import SMTP
import base64
import uuid
import smtplib

# Use the same test UUID as in conftest.py
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"

@pytest.fixture
def mock_smtp():
    """Mock SMTP server"""
    with patch('smtplib.SMTP') as mock:
        # Configure the context manager mock
        context = MagicMock()
        mock.return_value.__enter__.return_value = context
        mock.return_value.__exit__ = MagicMock()
        yield context

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

@pytest.mark.asyncio
async def test_send_upgrade_request_to_admin(mock_smtp, test_user):
    """Test sending upgrade request email to admin"""
    # Act
    result = await email_service.send_upgrade_request_to_admin(test_user, "Upgrade request")
    
    # Assert
    assert result is True
    assert mock_smtp.send_message.call_count == 1
    
    # Verify email content
    sent_email = mock_smtp.send_message.call_args[0][0]
    assert "Pro Plan Upgrade Request" in sent_email["Subject"]
    assert email_service.admin_email in sent_email["To"]

@pytest.mark.asyncio
async def test_send_upgrade_request_received(mock_smtp, test_user):
    """Test sending upgrade request received confirmation"""
    # Act
    result = await email_service.send_upgrade_request_received(test_user)
    
    # Assert
    assert result is True
    assert mock_smtp.send_message.call_count == 1
    
    # Verify email content
    sent_email = mock_smtp.send_message.call_args[0][0]
    assert "We've Received Your Pro Plan Upgrade Request" in sent_email["Subject"]
    assert test_user.email in sent_email["To"]

@pytest.mark.asyncio
async def test_send_upgrade_confirmation(mock_smtp, test_user):
    """Test sending upgrade confirmation email"""
    # Update user to Pro plan
    test_user.plan_type = PlanType.PRO
    test_user.credits = 500
    test_user.max_credits = 500
    
    # Act
    result = await email_service.send_upgrade_confirmation(test_user)
    
    # Assert
    assert result is True
    assert mock_smtp.send_message.call_count == 1
    
    # Verify email content
    sent_email = mock_smtp.send_message.call_args[0][0]
    assert "Welcome to Pro Plan!" in sent_email["Subject"]
    assert test_user.email in sent_email["To"]

@pytest.mark.asyncio
async def test_email_sending_failure(mock_smtp, test_user):
    """Test handling email sending failure"""
    # Setup mock to simulate failure
    mock_smtp.send_message.side_effect = smtplib.SMTPException("SMTP error")
    
    # Act and Assert
    result = await email_service.send_upgrade_request_to_admin(test_user, "Test message")
    assert result is False 