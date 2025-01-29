from typing import Optional
from pydantic import BaseModel, Field

class GenerateReplyRequest(BaseModel):
    """Request model for generating a reply to a LinkedIn post"""
    post_content: str = Field(..., min_length=1, max_length=3000, description="The content of the post to reply to")
    tone: Optional[str] = Field(None, description="The desired tone of the reply (e.g., professional, casual)")

class GenerateReplyResponse(BaseModel):
    """Response model for the generated reply"""
    reply: str = Field(..., description="The generated reply")
    credits_remaining: int = Field(..., description="Number of credits remaining after generation")

class GeneratePostRequest(BaseModel):
    """Request model for generating a new LinkedIn post"""
    topic: str = Field(..., min_length=1, max_length=500, description="The topic to generate a post about")
    tone: Optional[str] = Field(None, description="The desired tone of the post (e.g., professional, casual)")
    target_audience: Optional[str] = Field(None, description="Target audience for the post (e.g., developers, marketers)")
    key_points: Optional[list[str]] = Field(None, description="Key points to include in the post")
    max_length: Optional[int] = Field(1000, ge=100, le=3000, description="Maximum length of the generated post")

class GeneratePostResponse(BaseModel):
    """Response model for the generated post"""
    post_content: str = Field(..., description="The generated post content")
    credits_remaining: int = Field(..., description="Number of credits remaining after generation")

class RewritePostRequest(BaseModel):
    """Request model for rewriting an existing LinkedIn post"""
    post_content: str = Field(..., min_length=1, max_length=3000, description="The original post content to rewrite")
    tone: str = Field(..., description="The desired tone for the rewritten post (e.g., professional, casual, enthusiastic)")
    preserve_key_points: Optional[bool] = Field(True, description="Whether to preserve the main points of the original post")
    max_length: Optional[int] = Field(None, ge=100, le=3000, description="Maximum length of the rewritten post")
    additional_instructions: Optional[str] = Field(None, description="Any additional instructions for rewriting")

class RewritePostResponse(BaseModel):
    """Response model for the rewritten post"""
    rewritten_content: str = Field(..., description="The rewritten post content")
    credits_remaining: int = Field(..., description="Number of credits remaining after generation")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str = Field(..., description="Error message") 