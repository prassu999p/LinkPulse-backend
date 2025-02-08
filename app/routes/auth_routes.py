from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..utils.database import get_db
from ..middleware.auth import create_access_token, verify_password, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None

@router.post("/login")
async def login(user_data: UserLogin, db=Depends(get_db)):
    """Login user and return access token"""
    try:
        # Sign in with Supabase Auth
        auth_data = {
            "email": user_data.email,
            "password": user_data.password
        }
        auth_response = db.client.auth.sign_in_with_password(auth_data)
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get user details from our database
        user = await db.get_user_by_email(user_data.email)
        if not user:
            # Create user in our database if they don't exist
            user_data_db = {
                'user_id': auth_response.user.id,
                'email': user_data.email,
                'credits': db.settings.INITIAL_FREE_CREDITS,
                'notification_preferences': {
                    'email_notifications': True,
                    'credit_alerts': True
                }
            }
            
            # Insert into user_credits table
            insert_response = db.client.from_('user_credits').insert(user_data_db).execute()
            if not insert_response.data:
                raise HTTPException(status_code=500, detail="Failed to create user credits")
            
            user = {
                'id': auth_response.user.id,
                'email': user_data.email,
                'credits': db.settings.INITIAL_FREE_CREDITS,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "credits": user.get("credits", db.settings.INITIAL_FREE_CREDITS),
                "full_name": user.get("full_name"),
                "company": user.get("company"),
                "job_title": user.get("job_title")
            }
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        if "Invalid login credentials" in str(e):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register(user_data: UserRegister, db=Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create auth user with Supabase
        auth_response = db.client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "company": user_data.company,
                    "job_title": user_data.job_title
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create user in our database
        user_data_db = {
            'user_id': auth_response.user.id,
            'email': user_data.email,
            'credits': db.settings.INITIAL_FREE_CREDITS,
            'full_name': user_data.full_name,
            'company': user_data.company,
            'job_title': user_data.job_title,
            'notification_preferences': {
                'email_notifications': True,
                'credit_alerts': True
            }
        }
        
        # Insert into user_credits table
        insert_response = db.client.from_('user_credits').insert(user_data_db).execute()
        if not insert_response.data:
            # If user credits creation fails, delete the auth user
            try:
                db.client.auth.admin.delete_user(auth_response.user.id)
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to create user credits")
        
        return {
            "access_token": auth_response.session.access_token if auth_response.session else None,
            "token_type": "bearer",
            "user": {
                "id": str(auth_response.user.id),
                "email": user_data.email,
                "full_name": user_data.full_name,
                "company": user_data.company,
                "job_title": user_data.job_title,
                "credits": db.settings.INITIAL_FREE_CREDITS
            }
        }
    except Exception as e:
        print(f"Registration error: {str(e)}")
        if "User already registered" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/linkedin")
async def linkedin_auth():
    """LinkedIn OAuth handler - to be implemented"""
    pass