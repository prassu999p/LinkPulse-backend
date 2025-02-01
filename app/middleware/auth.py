from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.database import get_db, _db
from typing import Optional, Dict
import uuid
from fastapi import status
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from ..config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )

security = CustomHTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        print(f"Attempting to decode token: {token[:20]}...")  # Only print first 20 chars for security
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Successfully decoded token. Payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError as e:
        print(f"Token has expired: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
    except jwt.JWTError as e:
        print(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    except Exception as e:
        print(f"Unexpected error decoding token: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

async def verify_token(
    credentials: HTTPAuthorizationCredentials = None,
) -> str:
    """Verify the authentication token and return the user_id"""
    if not credentials:
        print("Missing authentication token")
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )
    
    try:
        print(f"Verifying token: {credentials.credentials[:20]}...")  # Only print first 20 chars for security
        payload = decode_token(credentials.credentials)
        print(f"Token payload: {payload}")
        
        user_id = payload.get("sub")
        if not user_id:
            print("Invalid token payload - no user_id")
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
            
        # Check if user exists
        try:
            user = await _db.get_user(user_id)
            if not user:
                print(f"User not found in database: {user_id}")
                # Create user profile if it doesn't exist
                user = await _db.create_user(user_id, {
                    'email': payload.get('email'),
                    'credits': 50  # Default credits
                })
                if not user:
                    print(f"Failed to create user profile: {user_id}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create user profile"
                    )
                print(f"Created new user profile for: {user_id}")
            else:
                print(f"User already exists: {user_id}")
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database error"
            )
        
        print(f"Token verified successfully for user: {user_id}")
        return user_id
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        print(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    except Exception as e:
        print(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Dict:
    """Get current user from token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = await verify_token(credentials)
        return {"id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        ) 