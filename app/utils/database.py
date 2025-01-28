from supabase import create_client, Client
from ..config import get_settings
from typing import Optional, Dict, Any

class Database:
    def __init__(self):
        self.settings = get_settings()
        self.client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user details from database"""
        try:
            response = self.client.table('users').select("*").eq('user_id', user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    async def create_user(self, user_id: str, auth_provider: str = 'email') -> Optional[Dict[str, Any]]:
        """Create a new user with initial credits"""
        try:
            user_data = {
                'user_id': user_id,
                'credits_remaining': self.settings.INITIAL_FREE_CREDITS,
                'auth_provider': auth_provider
            }
            response = self.client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    async def update_user_credits(self, user_id: str, credits: int) -> bool:
        """Update user's credit balance"""
        try:
            response = self.client.table('users').update(
                {'credits_remaining': credits}
            ).eq('user_id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating credits: {e}")
            return False

    async def log_transaction(self, user_id: str, credit_change: int, action_type: str) -> Optional[Dict[str, Any]]:
        """Log a credit transaction"""
        try:
            transaction_data = {
                'user_id': user_id,
                'credit_change': credit_change,
                'action_type': action_type
            }
            response = self.client.table('transactions').insert(transaction_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error logging transaction: {e}")
            return None

# Create a singleton instance
db = Database() 