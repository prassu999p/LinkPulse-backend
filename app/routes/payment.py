from fastapi import APIRouter, HTTPException, Request
from ..services.credit import CreditService
from ..utils.paddle import verify_paddle_webhook

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/paddle-webhook")
async def paddle_webhook(request: Request):
    """Handle Paddle payment webhook"""
    # Implementation will be added later
    pass 