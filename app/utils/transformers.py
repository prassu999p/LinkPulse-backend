from typing import Dict, Any, Optional
from ..models.user import UserProfile, UserStats, NotificationPreferences

def transform_db_to_user_profile(db_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform database user data to UserProfile model format"""
    if not db_data:
        return {}
        
    return {
        "id": db_data.get("user_id"),
        "email": db_data.get("email", db_data.get("auth_provider")),  # Fallback to auth_provider if email not present
        "full_name": db_data.get("full_name"),
        "company": db_data.get("company"),
        "job_title": db_data.get("job_title"),
        "linkedin_profile": db_data.get("linkedin_profile"),
        "preferred_tone": db_data.get("preferred_tone"),
        "notification_preferences": db_data.get("notification_preferences", {
            "email_notifications": True,
            "credit_alerts": True
        }),
        "created_at": db_data.get("created_at"),
        "updated_at": db_data.get("updated_at")
    }

def transform_db_to_user_stats(db_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform database stats data to UserStats model format"""
    if not db_data:
        return {}
        
    return {
        "total_posts_generated": db_data.get("total_posts_generated", 0),
        "total_credits_used": db_data.get("total_credits_used", 0),
        "remaining_credits": db_data.get("remaining_credits", 0),
        "last_login": db_data.get("last_login"),
        "account_created": db_data.get("created_at")
    } 