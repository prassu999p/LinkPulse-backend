from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..utils.database import get_db
from ..middleware.auth import create_access_token, verify_password, get_password_hash
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None

@router.post("/login")
async def login(user_data: UserLogin, db=Depends(get_db)):
    """Login user and return access token"""
    try:
        print(f"Login attempt for email: {user_data.email}")
        
        # Sign in with Supabase Auth
        auth_data = {
            "email": user_data.email,
            "password": user_data.password
        }
        print("Attempting Supabase auth...")
        
        try:
            auth_response = db.client.auth.sign_in_with_password(auth_data)
            print(f"Auth response: {auth_response}")
            if not auth_response.user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except Exception as auth_error:
            print(f"Auth error: {str(auth_error)}")
            if "Invalid login credentials" in str(auth_error):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            elif "Email not confirmed" in str(auth_error):
                raise HTTPException(status_code=403, detail="Please confirm your email address")
            else:
                raise HTTPException(status_code=500, detail="Authentication failed")
        
        # Get user details from our database
        print("Getting user details...")
        user = await db.get_user_by_email(user_data.email)
        print(f"User details: {user}")
        if not user:
            # Create user profile if it doesn't exist
            user_data_db = {
                'user_id': auth_response.user.id,
                'credits': db.settings.INITIAL_FREE_CREDITS,
                'full_name': auth_response.user.user_metadata.get('full_name'),
                'notification_preferences': {
                    'email_notifications': True,
                    'credit_alerts': True
                }
            }
            
            try:
                user = await db.create_user(auth_response.user.id, user_data_db)
                if not user:
                    raise HTTPException(status_code=500, detail="Failed to create user profile")
            except Exception as create_error:
                print(f"User creation error: {str(create_error)}")
                raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        # Create our own JWT token
        token_data = {
            "sub": auth_response.user.id,  # sub is standard JWT claim for subject (user id)
            "email": auth_response.user.email
        }
        token = create_access_token(token_data)
        
        return {
            "token": token,  # Our own JWT token
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "credits": user.get('credits', db.settings.INITIAL_FREE_CREDITS),
                "full_name": user.get('full_name'),
                "company": user.get('company'),
                "job_title": user.get('job_title'),
                "notification_preferences": user.get('notification_preferences', {
                    'email_notifications': True,
                    'credit_alerts': True
                })
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/register")
async def register(user_data: UserRegister, db=Depends(get_db)):
    """Register a new user"""
    try:
        print(f"Registration attempt for email: {user_data.email}")
        
        # Check if user already exists
        existing_user = await db.get_user_by_email(user_data.email)
        print(f"Existing user check result: {existing_user}")
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user in Supabase Auth
        try:
            print("Attempting to create auth user with admin client...")
            auth_response = db.admin_client.auth.admin.create_user({
                "email": user_data.email,
                "password": user_data.password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": user_data.full_name,
                    "company": user_data.company,
                    "job_title": user_data.job_title
                }
            })
            print(f"Auth user created: {auth_response.user.id}")
            
            # Create user profile in our database
            user_data_db = {
                'user_id': auth_response.user.id,
                'credits': db.settings.INITIAL_FREE_CREDITS,
                'full_name': user_data.full_name,
                'company': user_data.company,
                'job_title': user_data.job_title,
                'notification_preferences': {
                    'email_notifications': True,
                    'credit_alerts': True
                }
            }
            
            try:
                print("Creating user profile...")
                user = await db.create_user(auth_response.user.id, user_data_db)
                print(f"User profile created: {user}")
                if not user:
                    print("Failed to create user profile")
                    # Clean up auth user if profile creation fails
                    try:
                        db.admin_client.auth.admin.delete_user(auth_response.user.id)
                    except Exception as cleanup_error:
                        print(f"Failed to clean up auth user: {cleanup_error}")
                    raise HTTPException(status_code=500, detail="Failed to create user profile")
            except Exception as create_error:
                print(f"Error creating user profile: {create_error}")
                # Clean up auth user if profile creation fails
                try:
                    db.admin_client.auth.admin.delete_user(auth_response.user.id)
                except Exception as cleanup_error:
                    print(f"Failed to clean up auth user: {cleanup_error}")
                raise HTTPException(status_code=500, detail="Failed to create user profile")
            
            # Sign in the user to get the session
            sign_in_response = db.client.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if not sign_in_response.session:
                raise HTTPException(status_code=500, detail="Failed to sign in after registration")
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "token": sign_in_response.session.access_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "full_name": user_data.full_name,
                    "company": user_data.company,
                    "job_title": user_data.job_title,
                    "credits": db.settings.INITIAL_FREE_CREDITS,
                    "notification_preferences": {
                        "email_notifications": True,
                        "credit_alerts": True
                    }
                }
            }
            
        except Exception as auth_error:
            print(f"Auth error: {str(auth_error)}")
            raise HTTPException(status_code=500, detail=str(auth_error))
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/linkedin")
async def linkedin_auth():
    """Handle LinkedIn OAuth authentication"""
    # TODO: Implement LinkedIn OAuth
    raise HTTPException(status_code=501, detail="LinkedIn authentication not implemented yet") 