import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Сервис для работы с Groq AI"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY не найден в переменных окружения")
        
        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-20b"
    
    def get_cardio_analysis(self, age: int, pulse: int, risk: str, symptoms: str) -> str:
        """
        Получить анализ от AI кардиолога
        
        Args:
            age: Возраст пациента
            pulse: Пульс
            risk: Уровень риска
            symptoms: Симптомы
            
        Returns:
            str: Ответ от AI кардиолога
        """
        user_prompt = (
            f"Возраст: {age}\n"
            f"Пульс: {pulse}\n"
            f"Риск: {risk}\n"
            f"Симптомы: {symptoms}\n\n"
            f"Дай понятное объяснение состояния, советы по образу жизни и ответь как кардиолог."
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
            raise Exception(f"Ошибка при обращении к AI: {str(e)}")
    
    def get_health_advice(self, condition: str) -> str:
        """
        Получить общие советы по здоровью
        
        Args:
            condition: Описание состояния
            
        Returns:
            str: Советы по здоровью
        """
        user_prompt = (
            f"Состояние: {condition}\n\n"
            f"Дай общие советы по здоровью и образу жизни для этого состояния."
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
            raise Exception(f"Ошибка при обращении к AI: {str(e)}")
    
    def is_healthy(self) -> bool:
        """
        Проверить доступность AI сервиса
        
        Returns:
            bool: True если сервис доступен
        """
        try:
            # Простой тестовый запрос
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Тест"}],
                max_completion_tokens=10,
                stream=False
            )
            return True
        except:
            return False
