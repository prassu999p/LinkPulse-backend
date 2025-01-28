import pytest
from uuid import uuid4
from app.services.credit import credit_service
from app.utils.database import db

@pytest.mark.asyncio
async def test_initialize_user_credits():
    # Generate a random user ID for testing
    user_id = str(uuid4())
    
    # Initialize credits for new user
    success = await credit_service.initialize_user_credits(user_id)
    assert success == True
    
    # Verify credits were initialized
    credits = await credit_service.get_user_credits(user_id)
    assert credits == 10  # INITIAL_FREE_CREDITS value
    
    # Try to initialize again (should fail)
    success = await credit_service.initialize_user_credits(user_id)
    assert success == False

@pytest.mark.asyncio
async def test_credit_operations():
    # Create a test user
    user_id = str(uuid4())
    await credit_service.initialize_user_credits(user_id)
    
    # Test credit deduction
    success, new_credits = await credit_service.deduct_credits(user_id, 2)
    assert success == True
    assert new_credits == 8
    
    # Test credit addition
    success, new_credits = await credit_service.add_credits(user_id, 5)
    assert success == True
    assert new_credits == 13
    
    # Verify final balance
    credits = await credit_service.get_user_credits(user_id)
    assert credits == 13

@pytest.mark.asyncio
async def test_insufficient_credits():
    # Create a test user
    user_id = str(uuid4())
    await credit_service.initialize_user_credits(user_id)
    
    # Try to deduct more credits than available
    with pytest.raises(Exception) as exc_info:
        await credit_service.deduct_credits(user_id, 20)
    assert "Insufficient credits" in str(exc_info.value)
    
    # Verify balance remained unchanged
    credits = await credit_service.get_user_credits(user_id)
    assert credits == 10 