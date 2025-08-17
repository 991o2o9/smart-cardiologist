import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Service for working with Groq AI"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-20b"
    
    def get_cardio_analysis(self, age: int, pulse: int, risk: str, symptoms: str) -> str:
        """
        Get analysis from AI cardiologist
        
        Args:
            age: Patient age
            pulse: Pulse rate
            risk: Risk level
            symptoms: Symptoms
            
        Returns:
            str: Response from AI cardiologist
        """
        user_prompt = (
            f"Age: {age}\n"
            f"Pulse: {pulse}\n"
            f"Risk: {risk}\n"
            f"Symptoms: {symptoms}\n\n"
            f"Give a clear explanation of the condition, lifestyle advice and respond as a cardiologist."
        )
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
                max_completion_tokens=500,
                top_p=1,
                reasoning_effort="medium",
                stream=False
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error when contacting AI: {str(e)}")
    
    def get_health_advice(self, condition: str) -> str:
        """
        Get general health advice
        
        Args:
            condition: Condition description
            
        Returns:
            str: Health and lifestyle advice
        """
        user_prompt = (
            f"Condition: {condition}\n\n"
            f"Give general health and lifestyle advice for this condition."
        )
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
                max_completion_tokens=300,
                top_p=1,
                stream=False
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error when contacting AI: {str(e)}")
    
    def is_healthy(self) -> bool:
        """
        Check AI service availability
        
        Returns:
            bool: True if service is available
        """
        try:
            # Simple test request
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_completion_tokens=10,
                stream=False
            )
            return True
        except:
            return False
