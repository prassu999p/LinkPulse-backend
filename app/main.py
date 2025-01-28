from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from .middleware.auth import verify_token, security
from .services.credit import credit_service

app = FastAPI(
    title="LinkedIn Content Assistant API",
    description="API for generating and managing LinkedIn content",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to LinkedIn Content Assistant API"}

@app.get("/credits")
async def get_credits(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user's current credit balance"""
    try:
        user_id = await verify_token(credentials)
        credits = await credit_service.get_user_credits(user_id)
        return {"credits": credits}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/credits/initialize")
async def initialize_credits(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Initialize credits for a new user"""
    try:
        user_id = await verify_token(credentials)
        # First check if user already has credits
        try:
            existing_credits = await credit_service.get_user_credits(user_id)
            return {"message": "User already has credits initialized", "credits": existing_credits}
        except HTTPException:
            # User not found, proceed with initialization
            success = await credit_service.initialize_user_credits(user_id)
            if success:
                credits = await credit_service.get_user_credits(user_id)
                return {"message": "Credits initialized successfully", "credits": credits}
            raise HTTPException(status_code=500, detail="Failed to initialize credits")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 