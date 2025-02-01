from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class PlanType(Enum):
    BASIC = "basic"
    PRO = "pro"

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    credit_alerts: bool = True

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_profile: Optional[str] = None
    preferred_tone: Optional[str] = None
    notification_preferences: NotificationPreferences
    plan_type: PlanType = PlanType.BASIC
    credits: int = 50
    max_credits: int = 50
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_profile: Optional[str] = None
    preferred_tone: Optional[str] = None
    notification_preferences: Optional[NotificationPreferences] = None

class UserStats(BaseModel):
    total_posts_generated: int
    total_credits_used: int
    remaining_credits: int
    last_login: str
    account_created: str

    class Config:
        from_attributes = True

class Plan(BaseModel):
    type: PlanType
    credits: int
    max_credits: int
    price_usd: float

    @classmethod
    def get_basic_plan(cls) -> 'Plan':
        return cls(
            type=PlanType.BASIC,
            credits=50,
            max_credits=50,
            price_usd=0
        )

    @classmethod
    def get_pro_plan(cls) -> 'Plan':
        return cls(
            type=PlanType.PRO,
            credits=500,
            max_credits=500,
            price_usd=10.0
        ) 