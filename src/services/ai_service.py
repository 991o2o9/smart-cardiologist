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
            self.model = "openai/gpt-5-chat-latest"
            logger.info("AI Service initialized with GPT provider (AIMLAPI)")
            
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}. Use 'GROQ' or 'GPT'")
    
    def _analyze_question_complexity(self, question: str, conversation_history: list = None) -> dict:
        """
        Анализирует сложность вопроса для определения типа ответа с учетом контекста
        
        Args:
            question: Вопрос пользователя
            conversation_history: История диалога для анализа контекста
            
        Returns:
            dict: Информация о сложности вопроса
        """
        question_lower = question.lower()
        
        # Простые вопросы - фактические, короткие
        simple_patterns = [
            "что такое", "что это", "что означает", "что значит",
            "какая норма", "какой нормальный", "сколько должно быть",
            "what is", "what does", "what means", "what's the normal",
            "how many", "how much", "what's normal", "what's the range"
        ]
        
        # Сложные вопросы - требующие объяснений, рекомендаций
        complex_patterns = [
            "как лечить", "как избавиться", "как снизить", "как повысить",
            "как предотвратить", "как избежать", "как улучшить",
            "какие симптомы", "какие признаки", "когда обратиться",
            "how to treat", "how to reduce", "how to prevent", "how to improve",
            "what are the symptoms", "what are the signs", "when to see",
            "рекомендации", "советы", "что делать", "как быть",
            "recommendations", "advice", "what should I do", "how to"
        ]
        
        # Очень сложные вопросы - комплексные, многоаспектные
        very_complex_patterns = [
            "комплексный", "подробный", "детальный", "полный анализ",
            "comprehensive", "detailed", "complete analysis", "full assessment",
            "все аспекты", "все факторы", "все рекомендации",
            "all aspects", "all factors", "all recommendations"
        ]
        
        # Подсчитываем совпадения
        simple_count = sum(1 for pattern in simple_patterns if pattern in question_lower)
        complex_count = sum(1 for pattern in complex_patterns if pattern in question_lower)
        very_complex_count = sum(1 for pattern in very_complex_patterns if pattern in question_lower)
        
        # Дополнительные факторы
        word_count = len(question.split())
        has_medical_terms = any(term in question_lower for term in [
            "сердце", "давление", "пульс", "холестерин", "инфаркт", "стенокардия",
            "heart", "pressure", "pulse", "cholesterol", "heart attack", "angina"
        ])
        
        # Анализ контекста диалога
        context_complexity = 0
        if conversation_history and len(conversation_history) > 1:
            # Анализируем предыдущие сообщения на сложность
            for msg in conversation_history[-3:]:  # Последние 3 сообщения
                if msg.get("role") == "user":
                    content = msg.get("content", "").lower()
                    # Если в предыдущих сообщениях есть сложные медицинские термины
                    if any(term in content for term in ["диабет", "холестерин", "давление", "диабет", "cholesterol", "pressure", "diabetes"]):
                        context_complexity += 1
                    # Если есть множественные факторы риска
                    if content.count("и") > 2 or content.count("and") > 2:
                        context_complexity += 1
        
        # Определяем сложность с учетом контекста
        if very_complex_count > 0 or (complex_count >= 2 and word_count > 20) or context_complexity >= 2:
            complexity = "very_complex"
            max_tokens = 8000
            response_style = "comprehensive"
        elif complex_count > 0 or (simple_count == 0 and word_count > 15) or context_complexity >= 1:
            complexity = "complex"
            max_tokens = 4000
            response_style = "detailed"
        else:
            complexity = "simple"
            max_tokens = 1000
            response_style = "concise"
        
        logger.info(f"Анализ сложности вопроса: {complexity} (токены: {max_tokens}, стиль: {response_style}, контекст: {context_complexity})")
        
        return {
            "complexity": complexity,
            "max_tokens": max_tokens,
            "response_style": response_style,
            "word_count": word_count,
            "has_medical_terms": has_medical_terms,
            "simple_patterns": simple_count,
            "complex_patterns": complex_count,
            "very_complex_patterns": very_complex_count,
            "context_complexity": context_complexity
        }
    
    def _create_adaptive_prompt(self, question: str, complexity_info: dict) -> str:
        """
        Creates adaptive prompt based on question complexity
        
        Args:
            question: User question
            complexity_info: Complexity information
            
        Returns:
            str: Adaptive prompt
        """
        complexity = complexity_info["complexity"]
        response_style = complexity_info["response_style"]
        
        if complexity == "simple":
            prompt = f"""
            You are an experienced cardiologist. A patient asks a simple question: "{question}"
            
            GIVE A BRIEF AND ACCURATE ANSWER (maximum 2-3 sentences).
            
            Requirements:
            - Respond in the same language as the question
            - Provide a specific fact or definition
            - Do not add unnecessary explanations
            - Be precise and clear
            
            Examples of good brief answers:
            - "Normal resting heart rate is 60-100 beats per minute."
            - "Normal blood pressure is 120/80 mmHg."
            - "LDL cholesterol should be below 100 mg/dL."
            """
        
        elif complexity == "complex":
            prompt = f"""
            You are an experienced cardiologist. A patient asks: "{question}"
            
            PROVIDE A DETAILED ANSWER with practical recommendations.
            
            Answer structure:
            1. Brief explanation of the problem
            2. Main recommendations (3-5 points)
            3. When to see a doctor
            4. Preventive measures
            
            Requirements:
            - Respond in the same language as the question
            - Give practical advice
            - Explain causes and mechanisms
            - Be understandable for the patient
            """
        
        else:  # very_complex
            prompt = f"""
            You are an experienced cardiologist. A patient asks a complex question: "{question}"
            
            PROVIDE A COMPREHENSIVE AND DETAILED ANALYSIS.
            
            Answer structure:
            1. Detailed problem analysis
            2. Scientific explanation of mechanisms
            3. Detailed recommendations for all aspects
            4. Action plan and monitoring
            5. Preventive measures
            6. When and which doctor to see
            7. Additional examinations
            
            Requirements:
            - Respond in the same language as the question
            - Provide maximum complete information
            - Include scientific justifications
            - Provide step-by-step recommendations
            - Consider all aspects of the problem
            """
        
        return prompt
    
    def _create_adaptive_prompt_with_context(self, question: str, complexity_info: dict, conversation_history: list = None) -> str:
        """
        Creates adaptive prompt with conversation context
        
        Args:
            question: User question
            complexity_info: Complexity information
            conversation_history: Conversation history (last 3-5 messages)
            
        Returns:
            str: Adaptive prompt with context
        """
        complexity = complexity_info["complexity"]
        response_style = complexity_info["response_style"]
        
        # Prepare context information
        context_info = ""
        if conversation_history and len(conversation_history) > 0:
            # Take last 5 messages for context
            recent_messages = conversation_history[-5:]
            context_info = "\n\nCONVERSATION CONTEXT (recent messages):\n"
            for i, msg in enumerate(recent_messages, 1):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]  # Limit content length
                context_info += f"{i}. {role}: {content}\n"
            context_info += "\nIMPORTANT: Consider the conversation context when answering. If the patient refers to previous information, acknowledge it and provide relevant follow-up advice."
        
        if complexity == "simple":
            prompt = f"""
            You are an experienced cardiologist. A patient asks a simple question: "{question}"
            {context_info}
            
            GIVE A BRIEF AND ACCURATE ANSWER (maximum 2-3 sentences).
            
            Requirements:
            - Respond in the same language as the question
            - Provide a specific fact or definition
            - If the question refers to previous context, acknowledge it briefly
            - Do not add unnecessary explanations
            - Be precise and clear
            
            Examples of good brief answers:
            - "Normal resting heart rate is 60-100 beats per minute."
            - "Normal blood pressure is 120/80 mmHg."
            - "LDL cholesterol should be below 100 mg/dL."
            """
        
        elif complexity == "complex":
            prompt = f"""
            You are an experienced cardiologist. A patient asks: "{question}"
            {context_info}
            
            PROVIDE A DETAILED ANSWER with practical recommendations.
            
            Answer structure:
            1. Brief explanation of the problem
            2. Main recommendations (3-5 points)
            3. When to see a doctor
            4. Preventive measures
            
            Requirements:
            - Respond in the same language as the question
            - If the question refers to previous context, acknowledge it and build upon it
            - Give practical advice
            - Explain causes and mechanisms
            - Be understandable for the patient
            - Maintain conversation flow naturally
            """
        
        else:  # very_complex
            prompt = f"""
            You are an experienced cardiologist. A patient asks a complex question: "{question}"
            {context_info}
            
            PROVIDE A COMPREHENSIVE AND DETAILED ANALYSIS.
            
            Answer structure:
            1. Detailed problem analysis
            2. Scientific explanation of mechanisms
            3. Detailed recommendations for all aspects
            4. Action plan and monitoring
            5. Preventive measures
            6. When and which doctor to see
            7. Additional examinations
            
            Requirements:
            - Respond in the same language as the question
            - If the question refers to previous context, acknowledge it and provide comprehensive follow-up
            - Provide maximum complete information
            - Include scientific justifications
            - Provide step-by-step recommendations
            - Consider all aspects of the problem
            - Maintain natural conversation flow
            """
        
        return prompt
    
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
        
        messages = [
            {"role": "system", "content": (
                "You are an experienced cardiologist. "
                "Provide professional medical analysis and recommendations. "
                "Be thorough but concise. "
                "Always prioritize patient safety and recommend emergency care when appropriate."
            )},
            {"role": "user", "content": user_prompt}
        ]
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
        
        messages = [
            {"role": "system", "content": (
                "You are a healthcare advisor specializing in cardiology and general health. "
                "Provide practical, evidence-based lifestyle recommendations. "
                "Be encouraging and supportive while maintaining medical accuracy. "
                "Always emphasize when professional medical consultation is needed."
            )},
            {"role": "user", "content": user_prompt}
        ]
        return self._create_completion(messages, max_tokens=4000, temperature=0.7)
    
    def get_adaptive_response(self, question: str, conversation_history: list = None) -> str:
        """
        Получает адаптивный ответ в зависимости от сложности вопроса с учетом истории диалога
        
        Args:
            question: Вопрос пользователя
            conversation_history: История диалога (последние 3-5 сообщений)
            
        Returns:
            str: Адаптивный ответ от ИИ кардиолога
        """
        # Анализируем сложность вопроса с учетом контекста
        complexity_info = self._analyze_question_complexity(question, conversation_history)
        
        # Создаем адаптивный промпт с учетом контекста
        prompt = self._create_adaptive_prompt_with_context(question, complexity_info, conversation_history)
        
        # Получаем ответ с соответствующими настройками
        messages = [
            {"role": "system", "content": (
                "You are an experienced cardiologist assistant. "
                "Adapt answer length to question complexity. "
                "Be clear, patient-friendly, and professional. "
                "If the case is urgent (e.g., chest pain, severe shortness of breath), "
                "always recommend calling emergency services."
            )},
            {"role": "user", "content": prompt}
        ]
        response = self._create_completion(
            messages, 
            max_tokens=complexity_info["max_tokens"], 
            temperature=0.7
        )
        
        logger.info(f"Адаптивный ответ с контекстом: {complexity_info['complexity']} стиль, {len(response)} символов")
        
        return response
    
    def is_healthy(self) -> bool:
        """
        Check AI service availability
        
        Returns:
            bool: True if service is available
        """
        try:
            messages = [
                {"role": "system", "content": "You are a test assistant. Respond with 'OK'."},
                {"role": "user", "content": "Test"}
            ]
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
