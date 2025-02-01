from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class PlanType(Enum):
    BASIC = "basic"
    PRO = "pro"

class Plan(BaseModel):
    type: PlanType
    credits: int
    max_credits: int
    price_usd: float

    @classmethod
    def get_basic_plan(cls) -> 'Plan':
        return cls(
            type=PlanType.BASIC,
            credits=50,  # Initial credits
            max_credits=50,  # Maximum credits for basic plan
            price_usd=0  # Free plan
        )

    @classmethod
    def get_pro_plan(cls) -> 'Plan':
        return cls(
            type=PlanType.PRO,
            credits=500,  # Initial credits
            max_credits=500,  # Maximum credits for pro plan
            price_usd=10.0
        )

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    plan: PlanType
    credits: int
    max_credits: int

class UpgradeRequest(BaseModel):
    user_id: str
    email: EmailStr
    current_plan: PlanType
    message: Optional[str] = None 