from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.database import db
from typing import Optional, Dict

class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authentication token"
            )

security = CustomHTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = None) -> str:
    """Verify the authentication token and return the user_id"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )
    
    # Here you would typically verify the JWT token
    # For now, we'll just use the token as the user_id
    user_id = credentials.credentials
    
    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        # Initialize new user with free credits
        success = await db.create_user(user_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )
    
    return user_id

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get the current authenticated user"""
    user_id = await verify_token(credentials)
    return {"id": user_id} 