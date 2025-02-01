from app.config import settings
from app.models.user import Plan, PlanType, UserProfile
from app.utils.database import get_db
from typing import Tuple, Optional, Dict
from fastapi import HTTPException

class CreditService:
    async def initialize_user_credits(self, user_id: str) -> bool:
        """Initialize credits for a new user with Basic plan"""
        try:
            db = await get_db()
            basic_plan = Plan.get_basic_plan()
            success = await db.set_user_credits(user_id, basic_plan.credits)
            if success:
                # Log the initial credit allocation
                await db.log_credit_transaction(
                    user_id=user_id,
                    amount=basic_plan.credits,
                    action_type="INITIAL_ALLOCATION",
                    description="Initial free credits for new user"
                )
            return success
        except Exception as e:
            print(f"Failed to initialize credits: {str(e)}")
            return False

    async def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance"""
        db = await get_db()
        credits = await db.get_user_credits(user_id)
        if credits is None:
            # If no credits found, try to initialize them
            if await self.initialize_user_credits(user_id):
                return Plan.get_basic_plan().credits
            raise HTTPException(status_code=404, detail="User credits not found")
        return credits

    async def set_user_credits(self, user_id: str, credits: int, plan_type: PlanType = PlanType.BASIC) -> bool:
        """Set user's credit balance with plan limit check"""
        try:
            db = await get_db()
            # Get plan max credits
            max_credits = Plan.get_pro_plan().max_credits if plan_type == PlanType.PRO else Plan.get_basic_plan().max_credits
            
            # Ensure credits don't exceed plan limit
            if credits > max_credits:
                credits = max_credits
            
            current_credits = await self.get_user_credits(user_id)
            success = await db.set_user_credits(user_id, credits)
            
            if success:
                # Log the credit change
                change_amount = credits - current_credits
                await db.log_credit_transaction(
                    user_id=user_id,
                    amount=change_amount,
                    action_type="MANUAL_ADJUSTMENT",
                    description=f"Credit adjustment: {change_amount} (Plan: {plan_type.value})"
                )
            return success
        except Exception as e:
            print(f"Failed to set credits: {str(e)}")
            return False

    async def deduct_credits(self, user_id: str, amount: int) -> Tuple[bool, int]:
        """Deduct credits from user's balance and return remaining credits"""
        try:
            db = await get_db()
            current_credits = await self.get_user_credits(user_id)
            if current_credits < amount:
                return False, current_credits
            
            new_credits = current_credits - amount
            success = await db.set_user_credits(user_id, new_credits)
            
            if success:
                # Log the deduction
                await db.log_credit_transaction(
                    user_id=user_id,
                    amount=-amount,
                    action_type="USAGE",
                    description="Credits used for content generation"
                )
            return success, new_credits
        except Exception as e:
            print(f"Failed to deduct credits: {str(e)}")
            return False, 0

    async def has_sufficient_credits(self, user_id: str, required_credits: int) -> bool:
        """Check if user has sufficient credits"""
        try:
            current_credits = await self.get_user_credits(user_id)
            return current_credits >= required_credits
        except Exception:
            return False

    async def upgrade_to_pro(self, user_id: str) -> bool:
        """Upgrade user to Pro plan"""
        try:
            db = await get_db()
            pro_plan = Plan.get_pro_plan()
            success = await self.set_user_credits(user_id, pro_plan.credits, PlanType.PRO)
            
            if success:
                await db.log_credit_transaction(
                    user_id=user_id,
                    amount=pro_plan.credits,
                    action_type="PLAN_UPGRADE",
                    description="Upgraded to Pro plan"
                )
            return success
        except Exception as e:
            print(f"Failed to upgrade to pro: {str(e)}")
            return False

    async def get_user_plan(self, user_id: str) -> PlanType:
        """Get user's current plan based on their credits"""
        try:
            credits = await self.get_user_credits(user_id)
            basic_plan = Plan.get_basic_plan()
            return PlanType.PRO if credits > basic_plan.max_credits else PlanType.BASIC
        except Exception:
            return PlanType.BASIC

    async def get_credit_history(self, user_id: str) -> Dict:
        """Get user's credit history and current balance"""
        try:
            db = await get_db()
            return await db.get_user_plan_details(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

credit_service = CreditService() 