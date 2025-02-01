from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict
from pydantic import BaseModel
from ..utils.database import Database, get_db
from ..middleware.auth import get_current_user
from app.models.user import UserProfile, UserProfileUpdate, UserStats, NotificationPreferences, PlanType
from app.middleware.auth import get_current_user
from app.models.user_models import Plan, UpgradeRequest
from app.services.email_service import email_service
from app.services.credit import credit_service

router = APIRouter(prefix="/user", tags=["user"])

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    credit_alerts: bool = True

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_profile: Optional[str] = None
    preferred_tone: Optional[str] = None
    notification_preferences: NotificationPreferences
    created_at: str
    updated_at: str
    plan: PlanType
    credits: int
    max_credits: int

class UserStats(BaseModel):
    total_posts_generated: int
    total_credits_used: int
    remaining_credits: int
    last_login: str
    account_created: str

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict = Depends(get_current_user), db=Depends(get_db)):
    """Get user profile including plan details"""
    try:
        user = await db.get_user(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        updated_profile = await db.update_user_profile(current_user["id"], profile_update.dict(exclude_unset=True))
        if not updated_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return updated_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user: Dict = Depends(get_current_user), db=Depends(get_db)):
    try:
        stats = await db.get_user_stats(current_user["id"])
        if not stats:
            raise HTTPException(status_code=404, detail="User stats not found")
        return UserStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notification-preferences")
async def update_notification_preferences(
    preferences: Dict,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        updated = await db.update_notification_preferences(current_user["id"], preferences)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upgrade-request")
async def request_plan_upgrade(
    request: UpgradeRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Request an upgrade to the Pro plan"""
    if request.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to request upgrade for this user")
    
    # Get current user profile
    profile = await get_user_profile(current_user)
    
    # Check if already on Pro plan
    if profile.plan == PlanType.PRO:
        raise HTTPException(status_code=400, detail="User is already on Pro plan")
    
    # Send upgrade request email
    success = await email_service.send_upgrade_request(request)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send upgrade request")
    
    return {
        "message": "Upgrade request sent successfully. Our team will contact you soon.",
        "status": "pending"
    }

@router.post("/upgrade-confirm/{user_id}")
async def confirm_upgrade(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Confirm user upgrade to Pro plan (admin only)
    Note: In production, add proper admin authentication
    """
    try:
        # Get user profile
        profile = await get_user_profile({"id": user_id})
        
        # Update credits to Pro plan
        await credit_service.set_user_credits(user_id, Plan.get_pro_plan().credits)
        
        # Send confirmation email
        await email_service.send_upgrade_confirmation(profile.email, "Pro")
        
        return {
            "message": "User upgraded to Pro plan successfully",
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 