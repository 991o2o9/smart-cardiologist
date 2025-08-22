"""
Трёхуровневая система фильтрации медицинских вопросов:
1. Словарь ключевых слов → быстрый фильтр
2. ML-классификатор → контекстный фильтр  
3. LLM fallback → только для сложных случаев
"""

import logging
from typing import Tuple, Dict, Any
from utils.medical_keywords import quick_medical_filter
from services.ml_filter_service import get_medical_classifier
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class ThreeLevelMedicalFilter:
    def __init__(self):
        self.ai_service = AIService()
        self.ml_classifier = get_medical_classifier()
        
        # Пороги для принятия решений
        self.QUICK_FILTER_CONFIDENCE = 0.8  # Уверенность для быстрого ответа
        self.ML_CONFIDENCE_LOW = 0.35  # Нижний порог для ML (снижен для большей уверенности)
        self.ML_CONFIDENCE_HIGH = 0.65  # Верхний порог для ML (повышен для большей уверенности)
        
    def filter_question(self, text: str) -> Dict[str, Any]:
        """
        Трёхуровневая фильтрация вопроса
        Возвращает результат с метаданными о процессе фильтрации
        """
        result = {
            'is_medical': False,
            'confidence': 0.0,
            'method': 'unknown',
            'details': {}
        }
        
        # Уровень 1: Быстрый фильтр на основе ключевых слов
        quick_result, quick_confidence = quick_medical_filter(text)
        
        if quick_confidence >= self.QUICK_FILTER_CONFIDENCE:
            result['is_medical'] = quick_result
            result['confidence'] = quick_confidence
            result['method'] = 'keyword_filter'
            result['details'] = {
                'quick_filter_result': quick_result,
                'quick_filter_confidence': quick_confidence
            }
            logger.info(f"Быстрый фильтр: {quick_result} (уверенность: {quick_confidence:.3f})")
            return result
        
        # Уровень 2: ML-классификатор
        try:
            ml_result, ml_confidence = self.ml_classifier.predict(text)
            
            # Если ML уверен (высокая или низкая вероятность)
            if ml_confidence <= self.ML_CONFIDENCE_LOW or ml_confidence >= self.ML_CONFIDENCE_HIGH:
                result['is_medical'] = ml_result
                result['confidence'] = ml_confidence
                result['method'] = 'ml_classifier'
                result['details'] = {
                    'ml_result': ml_result,
                    'ml_confidence': ml_confidence,
                    'quick_filter_result': quick_result,
                    'quick_filter_confidence': quick_confidence
                }
                logger.info(f"ML-классификатор: {ml_result} (уверенность: {ml_confidence:.3f})")
                return result
            
            # Уровень 3: LLM fallback (только для неопределенных случаев)
            logger.info(f"ML не уверен (уверенность: {ml_confidence:.3f}), используем LLM")
            llm_result = self._llm_fallback(text)
            
            result['is_medical'] = llm_result
            result['confidence'] = ml_confidence  # Используем уверенность ML как базовую
            result['method'] = 'llm_fallback'
            result['details'] = {
                'llm_result': llm_result,
                'ml_result': ml_result,
                'ml_confidence': ml_confidence,
                'quick_filter_result': quick_result,
                'quick_filter_confidence': quick_confidence
            }
            logger.info(f"LLM fallback: {llm_result}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в ML-классификаторе: {e}")
            # Fallback к быстрому фильтру
            result['is_medical'] = quick_result
            result['confidence'] = quick_confidence
            result['method'] = 'keyword_filter_fallback'
            result['details'] = {
                'error': str(e),
                'quick_filter_result': quick_result,
                'quick_filter_confidence': quick_confidence
            }
            return result
    
    def _llm_fallback(self, text: str) -> bool:
        """
        LLM fallback для сложных случаев
        Использует AI сервис для определения медицинского характера вопроса
        """
        try:
            # Создаем более четкий промпт для определения медицинского вопроса
            prompt = f"""
            Ты эксперт по классификации медицинских вопросов. Определи, является ли следующий вопрос медицинским.

            Медицинский вопрос - это вопрос о:
            - Здоровье, болезнях, симптомах, лечении
            - Лекарствах, медикаментах, препаратах
            - Врачах, больницах, медицинских процедурах
            - Физическом или психическом состоянии
            - Медицинских тестах, анализах, диагнозах

            НЕ медицинский вопрос - это вопрос о:
            - Погоде, кулинарии, развлечениях
            - Технологиях, компьютерах, программировании
            - Общих знаниях, географии, истории
            - Личных отношениях, работе, учебе (если не связаны со здоровьем)

            Вопрос: "{text}"

            Ответь строго одним словом: "ДА" (медицинский) или "НЕТ" (не медицинский).
            """
            
            # Используем AI сервис для анализа
            response = self.ai_service.get_cardio_analysis(
                age=None, 
                pulse=None, 
                risk=None, 
                symptoms=prompt
            )
            
            # Парсим ответ
            response_lower = response.lower().strip()
            
            # Более точный парсинг ответа
            if any(word in response_lower for word in ['да', 'yes', 'медицинский', 'medical']):
                return True
            elif any(word in response_lower for word in ['нет', 'no', 'не медицинский', 'not medical']):
                return False
            else:
                # Если ответ неясен, используем дополнительную логику
                medical_indicators = ['health', 'medical', 'doctor', 'hospital', 'symptom', 'treatment', 'medicine', 'pain', 'disease', 'illness']
                non_medical_indicators = ['weather', 'cook', 'recipe', 'movie', 'computer', 'technology', 'capital', 'city', 'country']
                
                text_lower = text.lower()
                medical_score = sum(1 for word in medical_indicators if word in text_lower)
                non_medical_score = sum(1 for word in non_medical_indicators if word in text_lower)
                
                logger.warning(f"Неясный ответ LLM: {response}. Используем дополнительную логику.")
                return medical_score > non_medical_score
                
        except Exception as e:
            logger.error(f"Ошибка в LLM fallback: {e}")
            # В случае ошибки считаем медицинским для безопасности
            return True
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Получение статистики использования фильтров"""
        # Здесь можно добавить сбор статистики
        return {
            'total_requests': 0,
            'keyword_filter_usage': 0,
            'ml_classifier_usage': 0,
            'llm_fallback_usage': 0
        }

# Глобальный экземпляр фильтра
medical_filter = ThreeLevelMedicalFilter()

def get_medical_filter() -> ThreeLevelMedicalFilter:
    """Получение глобального экземпляра фильтра"""
    return medical_filter

def is_medical_question_three_level(text: str) -> bool:
    """
    Упрощенная функция для проверки медицинского вопроса
    Использует трёхуровневую систему фильтрации
    """
    result = medical_filter.filter_question(text)
    return result['is_medical']
