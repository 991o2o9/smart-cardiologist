"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CardioRequest(BaseModel):
    """Схема запроса для кардио-ассистента"""
    age: int = Field(..., ge=0, le=120, description="Возраст пациента")
    pulse: int = Field(..., ge=40, le=200, description="Пульс (уд/мин)")
    risk: str = Field(..., description="Уровень риска (низкий/средний/высокий)")
    symptoms: str = Field(..., min_length=1, description="Описание симптомов")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 45,
                "pulse": 85,
                "risk": "средний",
                "symptoms": "одышка при физической нагрузке, усталость"
            }
        }
    )


class CardioResponse(BaseModel):
    """Схема ответа кардио-ассистента"""
    cached: bool = Field(..., description="Ответ из кеша")
    response: str = Field(..., description="Ответ от AI кардиолога")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cached": False,
                "response": "**Краткое резюме (с точки зрения кардиолога)**..."
            }
        }
    )


class HeartData(BaseModel):
    """Схема данных для предсказания риска сердечных заболеваний"""
    age: int = Field(..., ge=0, le=120)
    sex: int = Field(..., ge=0, le=1)
    cp: int = Field(..., ge=0, le=3)
    trestbps: int = Field(..., ge=90, le=200)
    chol: int = Field(..., ge=100, le=600)
    fbs: int = Field(..., ge=0, le=1)
    restecg: int = Field(..., ge=0, le=2)
    thalach: int = Field(..., ge=70, le=200)
    exang: int = Field(..., ge=0, le=1)
    oldpeak: float = Field(..., ge=0.0, le=6.0)
    slope: int = Field(..., ge=0, le=2)
    ca: int = Field(..., ge=0, le=4)
    thal: int = Field(..., ge=0, le=3)
    pulse: int = Field(..., ge=40, le=200)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 45,
                "sex": 1,
                "cp": 1,
                "trestbps": 130,
                "chol": 250,
                "fbs": 0,
                "restecg": 0,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.0,
                "slope": 1,
                "ca": 0,
                "thal": 1,
                "pulse": 85
            }
        }
    )


class HeartPredictionResponse(BaseModel):
    """Схема ответа для предсказания риска"""
    risk: int = Field(..., ge=0, le=1, description="Риск (0 - низкий, 1 - высокий)")
    probability: float = Field(..., ge=0.0, le=1.0, description="Вероятность риска")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "risk": 1,
                "probability": 0.85
            }
        }
    )
