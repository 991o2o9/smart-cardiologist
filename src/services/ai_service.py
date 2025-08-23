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
    
    def _create_groq_completion(self, messages: list, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Create completion using Groq API"""
        import time
        start_time = time.time()
        timeout = 60  # Увеличиваем таймаут до 60 секунд для длинных ответов
        
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
    
    def _create_gpt_completion(self, messages: list, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Create completion using GPT API (AIMLAPI)"""
        import time
        start_time = time.time()
        timeout = 60  # Увеличиваем таймаут до 60 секунд для длинных ответов
        
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
    
    def _create_completion(self, messages: list, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Create completion using the selected provider"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.provider == "GROQ":
                    response = self._create_groq_completion(messages, max_tokens, temperature)
                elif self.provider == "GPT":
                    response = self._create_gpt_completion(messages, max_tokens, temperature)
                
                # Проверяем, что ответ не пустой и достаточно длинный
                if response and len(response.strip()) > 20:
                    # Улучшенная проверка на неполные ответы - только явные признаки обрезания
                    incomplete_patterns = [
                        "**",  # Незакрытые markdown
                        "###",  # Незакрытые заголовки
                        "****",  # Множественные звездочки
                        "..."   # Многоточие в конце
                    ]
                    
                    # Проверяем только конец ответа на явные признаки обрезания
                    response_end = response.strip()[-10:]  # Последние 10 символов
                    is_incomplete = any(pattern in response_end for pattern in incomplete_patterns)
                    
                    if not is_incomplete:
                        logger.info(f"Успешный ответ от {self.provider} длиной {len(response)} символов")
                        return response
                    else:
                        logger.warning(f"Ответ кажется неполным на попытке {attempt + 1}, повторяем...")
                        # Увеличиваем токены для повторной попытки
                        max_tokens = int(max_tokens * 1.2)
                        continue
                else:
                    logger.warning(f"Ответ слишком короткий на попытке {attempt + 1}, повторяем...")
                    continue
                    
            except Exception as e:
                logger.error(f"Ошибка на попытке {attempt + 1} при обращении к {self.provider} AI: {str(e)}")
                if attempt == max_retries - 1:  # Последняя попытка
                    raise Exception(f"Ошибка при обращении к {self.provider} AI после {max_retries} попыток: {str(e)}")
                continue
        
        # Если все попытки не удались, возвращаем запасной ответ
        logger.error("Все попытки повтора не удались, возвращаем запасной ответ")
        return (
            "Извините, но у меня возникли технические трудности с предоставлением полного ответа. "
            "Пожалуйста, попробуйте еще раз, или обратитесь к своему лечащему врачу для получения персональной медицинской консультации. "
            "Для общего здоровья сердца сосредоточьтесь на: поддержании здорового питания, регулярных физических упражнениях, "
            "управлении стрессом и отказе от курения."
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
        return self._create_completion(messages, max_tokens=6000, temperature=0.7)
    
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
        return self._create_completion(messages, max_tokens=4000, temperature=0.7)
    
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
