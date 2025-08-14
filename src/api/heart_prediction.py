from fastapi import APIRouter, HTTPException
from src.models.schemas import HeartData, HeartPredictionResponse
from src.services.ml_service import MLService

router = APIRouter(prefix="/heart-prediction", tags=["Heart Prediction"])

ml_service = MLService()

@router.post("/predict", response_model=HeartPredictionResponse)
async def predict_heart_risk(data: HeartData):
    """
    Предсказать риск сердечных заболеваний
    
    Принимает медицинские параметры пациента и возвращает оценку риска.
    """
    try:
        # Предсказание
        risk, probability = ml_service.predict_heart_risk(data.model_dump())
        
        return HeartPredictionResponse(risk=risk, probability=probability)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")

@router.get("/health")
async def health_check():
    """Проверка здоровья ML сервиса"""
    return {
        "status": "healthy" if ml_service.is_healthy() else "unhealthy",
        "model_info": ml_service.get_model_info()
    }

@router.get("/feature-importance")
async def get_feature_importance():
    """Получить важность признаков модели"""
    try:
        importance = ml_service.get_feature_importance()
        return {
            "feature_importance": importance,
            "top_features": list(importance.items())[:10]  # Топ-10 признаков
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при получении важности признаков: {str(e)}"
        )
