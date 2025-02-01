from supabase import create_client, Client
from ..config import get_settings
from typing import Optional, Dict, Any, Union
from datetime import datetime
from app.models.user import UserProfile, UserStats, NotificationPreferences, Plan, PlanType
from fastapi import HTTPException
import json

class Database:
    def __init__(self):
        self.settings = get_settings()
        # Client for regular operations (anon key)
        self.client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )
        # Admin client for user management (service_role key)
        self.admin_client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_SERVICE_KEY
        )

    def _get_user_id(self, user: Union[str, Dict]) -> str:
        """Extract user ID from either a string or a dictionary containing user information."""
        if isinstance(user, dict):
            return user.get('user_id')
        return user

    def _transform_db_to_user_profile(self, db_user: Dict) -> UserProfile:
        """Transform database user data to UserProfile model."""
        notification_prefs = NotificationPreferences(
            email_notifications=db_user.get('notification_preferences', {}).get('email_notifications', True),
            credit_alerts=db_user.get('notification_preferences', {}).get('credit_alerts', True)
        )
        
        # Get credits and determine plan type
        credits = db_user.get('credits', 50)
        plan_type = PlanType.PRO if credits > Plan.get_basic_plan().max_credits else PlanType.BASIC
        max_credits = Plan.get_pro_plan().max_credits if plan_type == PlanType.PRO else Plan.get_basic_plan().max_credits
        
        return UserProfile(
            id=db_user['user_id'],
            email=db_user['email'],
            full_name=db_user.get('full_name'),
            company=db_user.get('company'),
            job_title=db_user.get('job_title'),
            linkedin_profile=db_user.get('linkedin_profile'),
            preferred_tone=db_user.get('preferred_tone'),
            notification_preferences=notification_prefs,
            plan_type=plan_type,
            credits=credits,
            max_credits=max_credits,
            created_at=db_user.get('created_at', datetime.now().isoformat()),
            updated_at=db_user.get('updated_at', datetime.now().isoformat())
        )

    def _transform_db_to_user_stats(self, db_stats: Dict) -> UserStats:
        """Transform database stats to UserStats model."""
        return UserStats(
            total_posts_generated=db_stats.get('total_posts_generated', 0),
            total_credits_used=db_stats.get('total_credits_used', 0),
            remaining_credits=db_stats.get('remaining_credits', 0),
            last_login=db_stats.get('last_login', datetime.now().isoformat()),
            account_created=db_stats.get('account_created', datetime.now().isoformat())
        )

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email from Supabase database."""
        try:
            # First get the auth user
            auth_response = self.admin_client.auth.admin.list_users()
            auth_users = [user for user in auth_response if user.email == email]
            
            if not auth_users:
                return None
                
            auth_user = auth_users[0]
            
            # Then get the user profile
            profile_response = self.admin_client.table('user_profiles').select('*').eq('user_id', auth_user.id).execute()
            
            if not profile_response.data:
                # Create default profile if it doesn't exist
                profile_data = {
                    'user_id': auth_user.id,
                    'credits': self.settings.INITIAL_FREE_CREDITS,
                    'notification_preferences': {
                        'email_notifications': True,
                        'credit_alerts': True
                    }
                }
                profile_response = self.admin_client.table('user_profiles').insert(profile_data).execute()
            
            user_data = profile_response.data[0] if profile_response.data else {}
            
            # Combine auth user and profile data
            return {
                'user_id': auth_user.id,
                'email': auth_user.email,
                'credits': user_data.get('credits', self.settings.INITIAL_FREE_CREDITS),
                'full_name': auth_user.user_metadata.get('full_name'),
                'company': user_data.get('company'),
                'job_title': user_data.get('job_title'),
                'linkedin_profile': user_data.get('linkedin_profile'),
                'preferred_tone': user_data.get('preferred_tone'),
                'notification_preferences': user_data.get('notification_preferences'),
                'total_posts_generated': user_data.get('total_posts_generated', 0),
                'total_credits_used': user_data.get('total_credits_used', 0),
                'created_at': user_data.get('created_at', auth_user.created_at),
                'updated_at': user_data.get('updated_at', auth_user.updated_at)
            }
            
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            return None

    async def get_user(self, user: Union[str, Dict]) -> Optional[UserProfile]:
        """Get user profile from Supabase database."""
        try:
            user_id = self._get_user_id(user)
            
            # Get auth user
            auth_user = self.admin_client.auth.admin.get_user_by_id(user_id)
            if not auth_user:
                print(f"Auth user not found: {user_id}")
                return None
                
            # Get user profile
            profile_response = self.admin_client.table('user_profiles').select('*').eq('user_id', user_id).execute()
            profile_data = profile_response.data[0] if profile_response.data else {}
            
            print(f"Got auth user: {auth_user.user.id}")
            print(f"Got profile data: {profile_data}")
            
            # Combine data
            user_data = {
                'user_id': auth_user.user.id,
                'email': auth_user.user.email,
                'credits': profile_data.get('credits', self.settings.INITIAL_FREE_CREDITS),
                'full_name': auth_user.user.user_metadata.get('full_name'),
                'company': profile_data.get('company'),
                'job_title': profile_data.get('job_title'),
                'linkedin_profile': profile_data.get('linkedin_profile'),
                'preferred_tone': profile_data.get('preferred_tone'),
                'notification_preferences': profile_data.get('notification_preferences'),
                'total_posts_generated': profile_data.get('total_posts_generated', 0),
                'total_credits_used': profile_data.get('total_credits_used', 0),
                'created_at': profile_data.get('created_at', auth_user.user.created_at),
                'updated_at': profile_data.get('updated_at', auth_user.user.updated_at)
            }
            
            print(f"Combined user data: {user_data}")
            return self._transform_db_to_user_profile(user_data)
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    async def create_user(self, user_id: str, user_data: Dict) -> Optional[UserProfile]:
        """Create user profile in Supabase database."""
        try:
            print(f"Creating user profile for user_id: {user_id}")
            print(f"User data: {user_data}")
            
            # Get auth user to ensure it exists
            auth_user = self.admin_client.auth.admin.get_user_by_id(user_id)
            if not auth_user:
                print("Auth user not found")
                raise HTTPException(status_code=404, detail="Auth user not found")
            
            # Create user profile
            profile_data = {
                'user_id': user_id,
                'credits': user_data.get('credits', self.settings.INITIAL_FREE_CREDITS),
                'company': user_data.get('company'),
                'job_title': user_data.get('job_title'),
                'linkedin_profile': user_data.get('linkedin_profile'),
                'preferred_tone': user_data.get('preferred_tone'),
                'notification_preferences': user_data.get('notification_preferences', {
                    'email_notifications': True,
                    'credit_alerts': True
                }),
                'total_posts_generated': 0,
                'total_credits_used': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            print(f"Inserting profile data: {profile_data}")
            response = self.admin_client.table('user_profiles').insert(profile_data).execute()
            print(f"Insert response: {response}")
            
            if not response.data:
                print("Failed to create user profile - no data in response")
                raise HTTPException(status_code=500, detail="Failed to create user profile")
            
            # Return combined user data
            return self._transform_db_to_user_profile({
                'user_id': user_id,
                'email': auth_user.user.email,
                'credits': profile_data['credits'],
                'full_name': auth_user.user.user_metadata.get('full_name'),
                'company': profile_data['company'],
                'job_title': profile_data['job_title'],
                'linkedin_profile': profile_data['linkedin_profile'],
                'preferred_tone': profile_data['preferred_tone'],
                'notification_preferences': profile_data['notification_preferences'],
                'total_posts_generated': profile_data['total_posts_generated'],
                'total_credits_used': profile_data['total_credits_used'],
                'created_at': profile_data['created_at'],
                'updated_at': profile_data['updated_at']
            })
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_user_credits(self, user: Union[str, Dict], credits: int) -> bool:
        """Update user credits in Supabase database."""
        try:
            user_id = self._get_user_id(user)
            response = self.admin_client.table('user_profiles').update({'credits': credits}).eq('user_id', user_id).execute()
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"Error updating user credits: {str(e)}")
            return False

    async def update_user_profile(self, user: Union[str, Dict], profile_data: Dict) -> Optional[UserProfile]:
        """Update user profile in Supabase database."""
        try:
            user_id = self._get_user_id(user)
            profile_data['updated_at'] = datetime.now().isoformat()
            
            # Update profile data
            response = self.admin_client.table('user_profiles').update(profile_data).eq('user_id', user_id).execute()
            if not response.data:
                return None
                
            # Return updated user data
            return await self.get_user(user_id)
        except Exception as e:
            print(f"Error updating user profile: {str(e)}")
            return None

    async def log_transaction(self, user: Union[str, Dict], transaction_data: Dict) -> bool:
        """Log transaction in Supabase database."""
        try:
            user_id = self._get_user_id(user)
            transaction_data['user_id'] = user_id
            response = self.admin_client.table('transactions').insert(transaction_data).execute()
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"Error logging transaction: {str(e)}")
            return False

    async def get_user_stats(self, user: Union[str, Dict]) -> Optional[UserStats]:
        """Get user stats from Supabase database."""
        try:
            user_id = self._get_user_id(user)
            response = self.client.from_('user_stats').select('*').eq('user_id', user_id).execute()
            if response.data and len(response.data) > 0:
                return self._transform_db_to_user_stats(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user stats: {str(e)}")
            return None

    async def get_user_credits(self, user_id: str) -> Optional[int]:
        """Get user's credit balance from database"""
        try:
            response = self.client.table('user_credits').select('credits').eq('user_id', user_id).execute()
            if not response.data:
                return None
            return response.data[0]['credits']
        except Exception as e:
            print(f"Database error in get_user_credits: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def set_user_credits(self, user_id: str, credits: int) -> bool:
        """Set user's credit balance in database"""
        try:
            # Try to update existing record
            response = self.client.table('user_credits').update({
                'credits': credits,
                'updated_at': 'now()'
            }).eq('user_id', user_id).execute()

            # If no record exists, insert new one
            if not response.data:
                response = self.client.table('user_credits').insert({
                    'user_id': user_id,
                    'credits': credits,
                    'created_at': 'now()',
                    'updated_at': 'now()'
                }).execute()

            return bool(response.data)
        except Exception as e:
            print(f"Database error in set_user_credits: {str(e)}")
            return False

    async def get_user_plan_details(self, user_id: str) -> Optional[Dict]:
        """Get user's plan details including credits and history"""
        try:
            credits = await self.get_user_credits(user_id)
            if credits is None:
                return None

            # Get credit usage history
            history = self.client.table('credit_history').select(
                'amount', 'action_type', 'created_at'
            ).eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()

            return {
                'credits': credits,
                'history': history.data if history.data else []
            }
        except Exception as e:
            print(f"Database error in get_user_plan_details: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def log_credit_transaction(
        self,
        user_id: str,
        amount: int,
        action_type: str,
        description: Optional[str] = None
    ) -> bool:
        """Log credit transaction in history"""
        try:
            response = self.client.table('credit_history').insert({
                'user_id': user_id,
                'amount': amount,
                'action_type': action_type,
                'description': description,
                'created_at': 'now()'
            }).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Database error in log_credit_transaction: {str(e)}")
            return False

    async def update_notification_preferences(self, user: Union[str, Dict], preferences: Dict) -> bool:
        """Update user notification preferences in Supabase database."""
        try:
            user_id = self._get_user_id(user)
            response = self.admin_client.table('user_profiles').update({'notification_preferences': preferences}).eq('user_id', user_id).execute()
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"Error updating notification preferences: {str(e)}")
            return False

    async def delete_user(self, email: str) -> bool:
        """Delete user from both auth and profiles."""
        try:
            print(f"\nDeleting user with email: {email}")
            
            # First get the auth user
            auth_response = self.admin_client.auth.admin.list_users()
            auth_users = [user for user in auth_response if user.email == email]
            
            if not auth_users:
                print(f"No auth user found for email: {email}")
                return False
                
            auth_user = auth_users[0]
            user_id = auth_user.id
            print(f"Found user with ID: {user_id}")
            
            # Delete from user_profiles first
            try:
                print("Deleting from user_profiles...")
                profile_response = self.admin_client.table('user_profiles').delete().eq('user_id', user_id).execute()
                print(f"Profile deletion response: {profile_response.data}")
            except Exception as e:
                print(f"Error deleting profile: {str(e)}")
                
            # Delete from auth
            try:
                print("Deleting from auth...")
                self.admin_client.auth.admin.delete_user(user_id)
                print("Auth user deleted successfully")
            except Exception as e:
                print(f"Error deleting auth user: {str(e)}")
                return False
            
            # Verify deletion
            try:
                verify_profile = self.admin_client.table('user_profiles').select('*').eq('user_id', user_id).execute()
                verify_auth = self.admin_client.auth.admin.get_user_by_id(user_id)
                
                if verify_profile.data or verify_auth:
                    print("Warning: User not fully deleted")
                    return False
                    
                print(f"Successfully deleted user {email}")
                return True
            except Exception as e:
                print(f"Error verifying deletion: {str(e)}")
                return True  # Assume success if we can't verify (might mean user is actually deleted)
            
        except Exception as e:
            print(f"Error in delete_user: {str(e)}")
            return False

# Create a singleton instance
_db = Database()

async def get_db():
    return _db