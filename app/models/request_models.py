from pydantic import BaseModel, Field
from typing import Optional

class GenerateReplyRequest(BaseModel):
    post_text: str = Field(..., description="The text of the LinkedIn post to reply to")
    tone: str = Field(..., description="The desired tone for the reply")

class GeneratePostRequest(BaseModel):
    topic: str = Field(..., description="The topic to generate a post about")
    tone: str = Field(..., description="The desired tone for the post")

class RewritePostRequest(BaseModel):
    draft_text: str = Field(..., description="The text of the post to be rewritten")
    tone: str = Field(..., description="The desired tone for the rewritten post") 