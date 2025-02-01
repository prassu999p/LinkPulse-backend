import asyncio
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import Database
from app.config import Settings

async def main():
    settings = Settings()
    db = Database()
    db.settings = settings  # Set settings after initialization
    
    email = 'help.datasphere@gmail.com'
    
    # Check if user exists in auth
    print(f"\nChecking user: {email}")
    auth_response = db.admin_client.auth.admin.list_users()
    auth_users = [user for user in auth_response if user.email == email]
    if auth_users:
        print(f"Found in auth system: {auth_users[0].id}")
    else:
        print("Not found in auth system")
    
    # Check if user exists in profiles
    user = await db.get_user_by_email(email)
    if user:
        print(f"Found in profiles: {user}")
    else:
        print("Not found in profiles")

if __name__ == '__main__':
    asyncio.run(main())
