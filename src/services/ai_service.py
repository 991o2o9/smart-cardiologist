import os
import logging
from typing import Optional, Literal
from groq import Groq
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for working with AI providers (Groq and GPT)"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER.upper()
        
        if self.provider == "GROQ":
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.client = Groq(api_key=api_key)
            self.model = "openai/gpt-oss-20b"
            logger.info("AI Service initialized with Groq provider")
            
        elif self.provider == "GPT":
            api_key = settings.GPT_API_KEY
            if not api_key:
                raise ValueError("GPT_API_KEY not found in environment variables")
            self.client = OpenAI(
                base_url="https://api.aimlapi.com/v1",
                api_key=api_key,
            )
            self.model = "deepseek-chat"
            logger.info("AI Service initialized with GPT provider (AIMLAPI)")
            
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}. Use 'GROQ' or 'GPT'")
    
    def _create_groq_completion(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Create completion using Groq API"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            reasoning_effort="medium",
            stream=False
        )
        return completion.choices[0].message.content.strip()
    
    def _create_gpt_completion(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Create completion using GPT API (AIMLAPI)"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.7,
            frequency_penalty=1,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    
    def _create_completion(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Create completion using the selected provider"""
        try:
            if self.provider == "GROQ":
                return self._create_groq_completion(messages, max_tokens, temperature)
            elif self.provider == "GPT":
                return self._create_gpt_completion(messages, max_tokens, temperature)
        except Exception as e:
            logger.error(f"Error when contacting {self.provider} AI: {str(e)}")
            raise Exception(f"Error when contacting {self.provider} AI: {str(e)}")
    
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
        
        messages = [{"role": "user", "content": user_prompt}]
        return self._create_completion(messages, max_tokens=500, temperature=0.7)
    
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
        
        messages = [{"role": "user", "content": user_prompt}]
        return self._create_completion(messages, max_tokens=300, temperature=0.7)
    
    def is_healthy(self) -> bool:
        """
        Check AI service availability
        
        Returns:
            bool: True if service is available
        """
        try:
            messages = [{"role": "user", "content": "Test"}]
            if self.provider == "GROQ":
                self._create_groq_completion(messages, max_tokens=10)
            elif self.provider == "GPT":
                self._create_gpt_completion(messages, max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
            return False
    
    def get_provider_info(self) -> dict:
        """
        Get information about the current AI provider
        
        Returns:
            dict: Provider information
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "healthy": self.is_healthy()
        }
