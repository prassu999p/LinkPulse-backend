import pytest
from fastapi import HTTPException
from app.services.credit import credit_service

pytestmark = pytest.mark.asyncio

async def test_initialize_user_credits(test_user_id):
    # Initialize credits for new user
    success = await credit_service.initialize_user_credits(test_user_id)
    assert success == True

    # Verify credits were initialized
    credits = await credit_service.get_user_credits(test_user_id)
    assert credits == 10  # INITIAL_FREE_CREDITS value

async def test_credit_operations(test_user_id):
    # Initialize user
    await credit_service.initialize_user_credits(test_user_id)
    
    # Get initial credits
    initial_credits = await credit_service.get_user_credits(test_user_id)
    
    # Test credit deduction
    success, new_credits = await credit_service.deduct_credits(test_user_id, 2)
    assert success == True
    assert new_credits == initial_credits - 2
    
    # Verify updated credits
    current_credits = await credit_service.get_user_credits(test_user_id)
    assert current_credits == new_credits

async def test_insufficient_credits(test_user_id):
    # Initialize user
    await credit_service.initialize_user_credits(test_user_id)
    
    # Try to deduct more credits than available
    with pytest.raises(HTTPException) as exc_info:
        await credit_service.deduct_credits(test_user_id, 20)
    assert exc_info.value.status_code == 402
    assert "Insufficient credits" in exc_info.value.detail

async def test_get_nonexistent_user():
    with pytest.raises(HTTPException) as exc_info:
        await credit_service.get_user_credits("nonexistent-user")
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail 