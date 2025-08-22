from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


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
    """Схема данных для предсказания риска сердечных заболеваний
    Все поля являются необязательными. Отсутствующие значения будут автоматически
    заполнены средними значениями из обучающего датасета.
    """
    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Optional[int] = Field(None, ge=0, le=1)
    cp: Optional[int] = Field(None, ge=0, le=3)
    trestbps: Optional[int] = Field(None, ge=90, le=200)
    chol: Optional[int] = Field(None, ge=100, le=600)
    fbs: Optional[int] = Field(None, ge=0, le=1)
    restecg: Optional[int] = Field(None, ge=0, le=2)
    thalach: Optional[int] = Field(None, ge=70, le=200)
    exang: Optional[int] = Field(None, ge=0, le=1)
    oldpeak: Optional[float] = Field(None, ge=0.0, le=6.0)
    slope: Optional[int] = Field(None, ge=0, le=2)
    ca: Optional[int] = Field(None, ge=0, le=4)
    thal: Optional[int] = Field(None, ge=0, le=3)
    pulse: Optional[int] = Field(None, ge=40, le=200)

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
    accuracy: str = Field(..., description="Оценка точности результата в процентах")
    message: str = Field(..., description="Сообщение с пояснением точности")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "risk": 1,
                "probability": 0.85,
                "accuracy": "60%",
                "message": "Ваш результат точен примерно на 60%, так как часть данных была подставлена автоматически."
            }
        }
    )


class MedicalChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message text")

class MedicalChatRequest(BaseModel):
    messages: List[MedicalChatMessage] = Field(..., description="Chat history (user and assistant messages)")

class MedicalChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant reply")


class CardioChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class CardioChatSummary(BaseModel):
    id: int
    summary: str
    created_at: str
    updated_at: str

class CardioChatDetail(BaseModel):
    id: int
    messages: List[CardioChatMessage]
    summary: str
    created_at: str
    updated_at: str

class ActiveChatResponse(BaseModel):
    chat_id: int
    messages: List[CardioChatMessage]
    summary: str
    created_at: str
    updated_at: str

class CreateChatResponse(BaseModel):
    chat_id: int
    message: str = "Новый чат создан"

class DeleteChatResponse(BaseModel):
    message: str = "Чат успешно удален"

class DeleteAllChatsResponse(BaseModel):
    message: str = "Вся история чатов успешно удалена"
    deleted_count: int
