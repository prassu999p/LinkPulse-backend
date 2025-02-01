from ..config import get_settings
from ..utils.database import get_db
from typing import Optional, Tuple
from fastapi import HTTPException, Depends

class CreditService:
    def __init__(self):
        self.settings = get_settings()
        self._db = None

    @property
    async def db(self):
        if self._db is None:
            self._db = await get_db()
        return self._db

    async def get_user_credits(self, user_id: str) -> int:
        """Get the number of credits for a user"""
        try:
            db = await self.db
            user = await db.get_user(user_id)
            if not user:
                print(f"User not found: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            print(f"Got user profile: {user}")
            return user.credits
        except Exception as e:
            print(f"Error getting user credits: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get user credits: {str(e)}")

    async def has_sufficient_credits(self, user_id: str, amount: int = 1) -> bool:
        """Check if user has sufficient credits"""
        try:
            current_credits = await self.get_user_credits(user_id)
            return current_credits >= amount
        except HTTPException:
            return False

    async def deduct_credits(self, user_id: str, amount: int = 1) -> Tuple[bool, int]:
        """Deduct credits from a user's account and return success status and remaining credits"""
        current_credits = await self.get_user_credits(user_id)
        if current_credits < amount:
            raise HTTPException(status_code=402, detail="Insufficient credits")
        
        db = await self.db
        new_credits = current_credits - amount
        success = await db.update_user_credits(user_id, new_credits)
        if success:
            await db.log_transaction(user_id, {"amount": -amount, "type": "credit_deduction"})
            return True, new_credits
        raise HTTPException(status_code=500, detail="Failed to deduct credits")

    async def add_credits(self, user_id: str, amount: int) -> Tuple[bool, int]:
        """Add credits to a user's account and return success status and new balance"""
        current_credits = await self.get_user_credits(user_id)
        db = await self.db
        new_credits = current_credits + amount
        success = await db.update_user_credits(user_id, new_credits)
        if success:
            await db.log_transaction(user_id, {"amount": amount, "type": "credit_addition"})
            return True, new_credits
        raise HTTPException(status_code=500, detail="Failed to add credits")

    async def initialize_user_credits(self, user_id: str) -> bool:
        """Initialize credits for a new user"""
        db = await self.db
        user = await db.get_user(user_id)
        if user:
            return False  # User already exists
        
        user_data = {
            "email": f"user_{user_id}@example.com",  # Placeholder email
            "credits": self.settings.INITIAL_FREE_CREDITS,
            "notification_preferences": {
                "email_notifications": True,
                "credit_alerts": True
            }
        }
        new_user = await db.create_user(user_id, user_data)
        if new_user:
            await db.log_transaction(
                user_id, 
                {
                    "amount": self.settings.INITIAL_FREE_CREDITS,
                    "type": "initial_credits"
                }
            )
            return True
        return False

# Create a singleton instance
credit_service = CreditService() 