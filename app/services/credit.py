from ..config import get_settings
from ..utils.database import db
from typing import Optional, Tuple
from fastapi import HTTPException

class CreditService:
    def __init__(self):
        self.settings = get_settings()

    async def get_user_credits(self, user_id: str) -> int:
        """Get the number of credits for a user"""
        user = await db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user['credits_remaining']

    async def has_sufficient_credits(self, user_id: str, amount: int = 1) -> bool:
        """Check if user has sufficient credits"""
        try:
            current_credits = await self.get_user_credits(user_id)
            return current_credits >= amount
        except HTTPException:
            return False

    async def deduct_credits(self, user_id: str, amount: int = 1) -> int:
        """Deduct credits from a user's account and return remaining credits"""
        current_credits = await self.get_user_credits(user_id)
        if current_credits < amount:
            raise HTTPException(status_code=400, detail="Insufficient credits")
        
        new_credits = current_credits - amount
        success = await db.update_user_credits(user_id, new_credits)
        if success:
            await db.log_transaction(user_id, -amount, "credit_deduction")
            return new_credits
        raise HTTPException(status_code=500, detail="Failed to deduct credits")

    async def add_credits(self, user_id: str, amount: int) -> int:
        """Add credits to a user's account and return new balance"""
        current_credits = await self.get_user_credits(user_id)
        new_credits = current_credits + amount
        success = await db.update_user_credits(user_id, new_credits)
        if success:
            await db.log_transaction(user_id, amount, "credit_addition")
            return new_credits
        raise HTTPException(status_code=500, detail="Failed to add credits")

    async def initialize_user_credits(self, user_id: str) -> bool:
        """Initialize credits for a new user"""
        user = await db.get_user(user_id)
        if user:
            return False  # User already exists
        
        new_user = await db.create_user(user_id)
        if new_user:
            await db.log_transaction(
                user_id, 
                self.settings.INITIAL_FREE_CREDITS, 
                "initial_credits"
            )
            return True
        return False

# Create a singleton instance
credit_service = CreditService() 