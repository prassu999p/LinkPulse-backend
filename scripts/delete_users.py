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

    # Delete all users
    print("Deleting all users...")
    try:
        deleted_count = db.client.from_('users').delete().execute()  # Delete all users without any condition
        print(f"Deleted {deleted_count} users from the database.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())
