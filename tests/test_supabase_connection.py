import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"URL: {supabase_url}")
    print(f"Key length: {len(supabase_key) if supabase_key else 0}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Try to fetch data
        response = supabase.table('users').select("*").execute()
        print("Connection successful!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False

if __name__ == "__main__":
    test_connection() 