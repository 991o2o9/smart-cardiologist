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
        import time
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            reasoning_effort="medium",
            stream=False
        )
        
        # Check timeout
        if time.time() - start_time > timeout:
            raise Exception("Request timeout exceeded")
            
        return completion.choices[0].message.content.strip()
    
    def _create_gpt_completion(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Create completion using GPT API (AIMLAPI)"""
        import time
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.7,
            frequency_penalty=1,
            max_tokens=max_tokens,
        )
        
        # Check timeout
        if time.time() - start_time > timeout:
            raise Exception("Request timeout exceeded")
            
        return response.choices[0].message.content.strip()
    
    def _create_completion(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Create completion using the selected provider"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.provider == "GROQ":
                    response = self._create_groq_completion(messages, max_tokens, temperature)
                elif self.provider == "GPT":
                    response = self._create_gpt_completion(messages, max_tokens, temperature)
                
                # Check if response seems complete (not cut off mid-sentence)
                if response and len(response.strip()) > 50:
                    # Check for common incomplete patterns
                    incomplete_patterns = [
                        "**", "##", "###", "####", "****", "*****",  # Unfinished markdown
                        "...", "..", ".",  # Dots at the end
                        "**3. Weight", "**4.", "**5.",  # Unfinished numbered lists
                        "Below is a", "Here are some", "Additional"  # Unfinished sentences
                    ]
                    
                    is_incomplete = any(pattern in response for pattern in incomplete_patterns)
                    
                    if not is_incomplete:
                        return response
                    else:
                        logger.warning(f"Response appears incomplete on attempt {attempt + 1}, retrying...")
                        # Increase tokens for retry
                        max_tokens = int(max_tokens * 1.5)
                        continue
                else:
                    logger.warning(f"Response too short on attempt {attempt + 1}, retrying...")
                    continue
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1} when contacting {self.provider} AI: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    raise Exception(f"Error when contacting {self.provider} AI after {max_retries} attempts: {str(e)}")
                continue
        
        # If all retries failed, return a fallback response
        logger.error("All retry attempts failed, returning fallback response")
        return (
            "I apologize, but I'm experiencing technical difficulties providing a complete response. "
            "Please try again, or contact your healthcare provider for personalized medical advice. "
            "For general heart health, focus on: maintaining a healthy diet, regular exercise, "
            "managing stress, and avoiding smoking."
        )
    
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
            f"Please provide a comprehensive cardiological analysis including:\n"
            f"1. Brief assessment of the current condition\n"
            f"2. Specific lifestyle recommendations (diet, exercise, stress management)\n"
            f"3. When to seek medical attention\n"
            f"4. Preventive measures\n\n"
            f"Respond as a professional cardiologist with clear, actionable advice. "
            f"Keep the response comprehensive but well-structured."
        )
        
        messages = [{"role": "user", "content": user_prompt}]
        return self._create_completion(messages, max_tokens=2000, temperature=0.7)
    
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
            f"Please provide comprehensive health and lifestyle advice including:\n"
            f"1. Dietary recommendations\n"
            f"2. Exercise guidelines\n"
            f"3. Lifestyle modifications\n"
            f"4. Preventive measures\n"
            f"5. When to consult a healthcare provider\n\n"
            f"Give practical, actionable advice that people can implement in their daily lives. "
            f"Structure the response clearly with bullet points or numbered lists."
        )
        
        messages = [{"role": "user", "content": user_prompt}]
        return self._create_completion(messages, max_tokens=1500, temperature=0.7)
    
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
