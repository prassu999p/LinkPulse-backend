from app.utils.database import CREATE_TABLES_SQL
from app.config import settings
from supabase import create_client
import asyncio

async def init_database():
    """Initialize database tables and policies"""
    try:
        # Connect to Supabase
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Split SQL into individual statements
        sql_statements = [stmt.strip() for stmt in CREATE_TABLES_SQL.split(';') if stmt.strip()]
        
        # Execute each statement
        for statement in sql_statements:
            try:
                client.table('user_credits').select('*').execute()
                print(f"Executed SQL: {statement[:50]}...")
            except Exception as e:
                print(f"Error executing statement: {str(e)}")
                print(f"Statement: {statement}")
                raise
        
        print("Database initialization completed successfully!")
        return True
    except Exception as e:
        print(f"Failed to initialize database: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(init_database()) 