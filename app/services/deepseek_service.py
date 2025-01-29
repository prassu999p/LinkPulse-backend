from typing import Optional, List
import httpx
from fastapi import HTTPException
from app.config import settings

class DeepSeekService:
    """Service class for interacting with DeepSeek API"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"  # Replace with actual DeepSeek API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_reply(self, post_content: str, tone: Optional[str] = None) -> str:
        """
        Generate a reply for a LinkedIn post
        
        Args:
            post_content (str): The content of the post to reply to
            tone (Optional[str]): The desired tone of the reply (e.g., professional, casual)
            
        Returns:
            str: The generated reply
            
        Raises:
            HTTPException: If the API call fails
        """
        try:
            tone_instruction = f" in a {tone} tone" if tone else ""
            prompt = f"""Generate a thoughtful and engaging LinkedIn reply to the following post{tone_instruction}. 
            The reply should be professional, add value to the conversation, and encourage engagement:
            
            Post: {post_content}
            """
            
            return await self._generate_content(prompt)
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate reply: {str(e)}"
            )

    async def generate_post(
        self,
        topic: str,
        tone: Optional[str] = None,
        target_audience: Optional[str] = None,
        key_points: Optional[List[str]] = None,
        max_length: Optional[int] = 1000
    ) -> str:
        """
        Generate a new LinkedIn post
        
        Args:
            topic (str): The topic to generate a post about
            tone (Optional[str]): The desired tone of the post
            target_audience (Optional[str]): Target audience for the post
            key_points (Optional[List[str]]): Key points to include in the post
            max_length (Optional[int]): Maximum length of the generated post
            
        Returns:
            str: The generated post content
            
        Raises:
            HTTPException: If the API call fails
        """
        try:
            tone_instruction = f" in a {tone} tone" if tone else ""
            audience_instruction = f" targeting {target_audience}" if target_audience else ""
            points_instruction = ""
            if key_points:
                points_list = "\n".join([f"- {point}" for point in key_points])
                points_instruction = f"\n\nInclude the following key points:\n{points_list}"
            
            prompt = f"""Generate an engaging and professional LinkedIn post about {topic}{tone_instruction}{audience_instruction}.
            The post should be informative, encourage discussion, and be no longer than {max_length} characters.
            Focus on providing value to the readers and maintaining a conversational yet professional style.{points_instruction}
            
            Include relevant hashtags at the end of the post.
            """
            
            return await self._generate_content(prompt)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate post: {str(e)}"
            )

    async def rewrite_post(
        self,
        post_content: str,
        tone: str,
        preserve_key_points: bool = True,
        max_length: Optional[int] = None,
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        Rewrite an existing LinkedIn post
        
        Args:
            post_content (str): The original post content to rewrite
            tone (str): The desired tone for the rewritten post
            preserve_key_points (bool): Whether to preserve the main points of the original post
            max_length (Optional[int]): Maximum length of the rewritten post
            additional_instructions (Optional[str]): Any additional instructions for rewriting
            
        Returns:
            str: The rewritten post content
            
        Raises:
            HTTPException: If the API call fails
        """
        try:
            length_instruction = f" The rewritten post should be no longer than {max_length} characters." if max_length else ""
            preserve_points_instruction = """
            Analyze the original post and ensure all key points and main messages are preserved in the rewritten version.
            """ if preserve_key_points else ""
            additional_instruction = f"\nAdditional instructions: {additional_instructions}" if additional_instructions else ""
            
            prompt = f"""Rewrite the following LinkedIn post in a {tone} tone while maintaining its professional nature.{length_instruction}
            {preserve_points_instruction}
            The rewritten post should be engaging, clear, and maintain the original message's intent.{additional_instruction}
            
            Original post:
            {post_content}
            
            Ensure the rewritten post includes relevant hashtags at the end.
            """
            
            return await self._generate_content(prompt)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to rewrite post: {str(e)}"
            )
    
    async def _generate_content(self, prompt: str) -> str:
        """
        Internal method to handle API calls to DeepSeek
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: The generated content
            
        Raises:
            HTTPException: If the API call fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "deepseek-chat",  # Replace with actual model name
                        "messages": [
                            {"role": "system", "content": "You are a professional LinkedIn content assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"DeepSeek API error: {response.text}"
                    )
                
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error communicating with DeepSeek API: {str(e)}"
            ) 