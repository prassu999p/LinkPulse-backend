from fastapi import APIRouter, Depends, HTTPException
from app.models.content_models import (
    GenerateReplyRequest,
    GenerateReplyResponse,
    GeneratePostRequest,
    GeneratePostResponse,
    RewritePostRequest,
    RewritePostResponse,
    ErrorResponse
)
from app.services.deepseek_service import DeepSeekService
from app.services.credit import credit_service
from app.middleware.auth import get_current_user
from typing import Dict

router = APIRouter(prefix="/content", tags=["content"])
deepseek_service = DeepSeekService()

@router.post(
    "/reply",
    response_model=GenerateReplyResponse,
    responses={
        401: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_reply(
    request: GenerateReplyRequest,
    current_user: Dict = Depends(get_current_user)
) -> GenerateReplyResponse:
    """
    Generate a reply to a LinkedIn post.
    Requires 1 credit per generation.
    """
    # Check if user has enough credits
    if not await credit_service.has_sufficient_credits(current_user["id"], 1):
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase more credits to continue."
        )
    
    try:
        # Generate reply using DeepSeek
        reply = await deepseek_service.generate_reply(
            post_content=request.post_content,
            tone=request.tone
        )
        
        # Deduct 1 credit
        credits_remaining = await credit_service.deduct_credits(current_user["id"], 1)
        
        return GenerateReplyResponse(
            reply=reply,
            credits_remaining=credits_remaining
        )
        
    except Exception as e:
        # If generation fails, don't deduct credits
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate reply: {str(e)}"
        )

@router.post(
    "/post",
    response_model=GeneratePostResponse,
    responses={
        401: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_post(
    request: GeneratePostRequest,
    current_user: Dict = Depends(get_current_user)
) -> GeneratePostResponse:
    """
    Generate a new LinkedIn post.
    Requires 1 credit per generation.
    """
    # Check if user has enough credits
    if not await credit_service.has_sufficient_credits(current_user["id"], 1):
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase more credits to continue."
        )
    
    try:
        # Generate post using DeepSeek
        post_content = await deepseek_service.generate_post(
            topic=request.topic,
            tone=request.tone,
            target_audience=request.target_audience,
            key_points=request.key_points,
            max_length=request.max_length
        )
        
        # Deduct 1 credit
        credits_remaining = await credit_service.deduct_credits(current_user["id"], 1)
        
        return GeneratePostResponse(
            post_content=post_content,
            credits_remaining=credits_remaining
        )
        
    except Exception as e:
        # If generation fails, don't deduct credits
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate post: {str(e)}"
        )

@router.post(
    "/rewrite",
    response_model=RewritePostResponse,
    responses={
        401: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def rewrite_post(
    request: RewritePostRequest,
    current_user: Dict = Depends(get_current_user)
) -> RewritePostResponse:
    """
    Rewrite an existing LinkedIn post in a different tone.
    Requires 1 credit per rewrite.
    """
    # Check if user has enough credits
    if not await credit_service.has_sufficient_credits(current_user["id"], 1):
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase more credits to continue."
        )
    
    try:
        # Rewrite post using DeepSeek
        rewritten_content = await deepseek_service.rewrite_post(
            post_content=request.post_content,
            tone=request.tone,
            preserve_key_points=request.preserve_key_points,
            max_length=request.max_length,
            additional_instructions=request.additional_instructions
        )
        
        # Deduct 1 credit
        credits_remaining = await credit_service.deduct_credits(current_user["id"], 1)
        
        return RewritePostResponse(
            rewritten_content=rewritten_content,
            credits_remaining=credits_remaining
        )
        
    except Exception as e:
        # If rewriting fails, don't deduct credits
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rewrite post: {str(e)}"
        ) 