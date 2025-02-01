from app.config import settings
from supabase import create_client
import asyncio
import os
import httpx

async def update_database():
    """Apply database schema updates"""
    try:
        # Connect to Supabase
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Read the update script
        update_script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'database',
            'update_schema.sql'
        )
        
        with open(update_script_path, 'r') as f:
            update_sql = f.read()

        # Execute the SQL directly using Supabase's REST API
        headers = {
            'apikey': settings.SUPABASE_KEY,
            'Authorization': f'Bearer {settings.SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"{settings.SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql_query': update_sql}
            )

            if response.status_code == 200:
                print("Database update completed successfully!")
                return True
            else:
                print(f"Failed to update database. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"Failed to update database: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(update_database()) 