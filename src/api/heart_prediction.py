from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.schemas import HeartData, HeartPredictionResponse
from src.models.database import User, HeartPrediction
from src.services.ml_service import MLService
from src.services.database import get_db
from src.services.encryption_service import encryption_service
from src.utils.auth_middleware import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/heart-prediction", tags=["Heart Prediction"])

ml_service = MLService()

@router.post("/predict", response_model=HeartPredictionResponse)
async def predict_heart_risk(
    data: HeartData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Предсказать риск сердечных заболеваний
    
    Требует авторизации.
    
    Принимает медицинские параметры пациента и возвращает оценку риска.
    """
    try:
        # Предсказание
        risk, probability = ml_service.predict_heart_risk(data.model_dump())
        
        # Шифруем данные перед сохранением
        encrypted_data = encryption_service.encrypt_medical_data({
            'age': data.age,
            'sex': data.sex,
            'cp': data.cp,
            'trestbps': data.trestbps,
            'chol': data.chol,
            'fbs': data.fbs,
            'restecg': data.restecg,
            'thalach': data.thalach,
            'exang': data.exang,
            'oldpeak': data.oldpeak,
            'slope': data.slope,
            'ca': data.ca,
            'thal': data.thal,
            'pulse': data.pulse,
            'risk_prediction': risk,
            'probability': probability
        })
        
        # Сохраняем в базу данных
        prediction = HeartPrediction(
            user_id=current_user.id,
            age=encrypted_data['age'],
            sex=encrypted_data['sex'],
            cp=encrypted_data['cp'],
            trestbps=encrypted_data['trestbps'],
            chol=encrypted_data['chol'],
            fbs=encrypted_data['fbs'],
            restecg=encrypted_data['restecg'],
            thalach=encrypted_data['thalach'],
            exang=encrypted_data['exang'],
            oldpeak=encrypted_data['oldpeak'],
            slope=encrypted_data['slope'],
            ca=encrypted_data['ca'],
            thal=encrypted_data['thal'],
            pulse=encrypted_data['pulse'],
            risk_prediction=encrypted_data['risk_prediction'],
            probability=encrypted_data['probability']
        )
        
        db.add(prediction)
        await db.commit()
        
        logger.info(f"Heart prediction saved for user {current_user.id}")
        
        return HeartPredictionResponse(risk=risk, probability=probability)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")


@router.get("/history", response_model=list[dict])
async def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Получить историю предсказаний пользователя
    
    Требует авторизации.
    
    - **limit**: Количество записей (по умолчанию 10)
    - **offset**: Смещение (по умолчанию 0)
    """
    try:
        # Получаем историю предсказаний
        result = await db.execute(
            select(HeartPrediction)
            .where(HeartPrediction.user_id == current_user.id)
            .order_by(HeartPrediction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        predictions = result.scalars().all()
        
        # Формируем ответ с расшифровкой данных
        history = []
        for prediction in predictions:
            # Расшифровываем данные
            decrypted_data = encryption_service.decrypt_medical_data({
                'age': prediction.age,
                'sex': prediction.sex,
                'cp': prediction.cp,
                'trestbps': prediction.trestbps,
                'chol': prediction.chol,
                'fbs': prediction.fbs,
                'restecg': prediction.restecg,
                'thalach': prediction.thalach,
                'exang': prediction.exang,
                'oldpeak': prediction.oldpeak,
                'slope': prediction.slope,
                'ca': prediction.ca,
                'thal': prediction.thal,
                'pulse': prediction.pulse,
                'risk_prediction': prediction.risk_prediction,
                'probability': prediction.probability
            })
            
            history.append({
                "id": prediction.id,
                "age": decrypted_data['age'],
                "sex": decrypted_data['sex'],
                "cp": decrypted_data['cp'],
                "trestbps": decrypted_data['trestbps'],
                "chol": decrypted_data['chol'],
                "fbs": decrypted_data['fbs'],
                "restecg": decrypted_data['restecg'],
                "thalach": decrypted_data['thalach'],
                "exang": decrypted_data['exang'],
                "oldpeak": decrypted_data['oldpeak'],
                "slope": decrypted_data['slope'],
                "ca": decrypted_data['ca'],
                "thal": decrypted_data['thal'],
                "pulse": decrypted_data['pulse'],
                "risk_prediction": decrypted_data['risk_prediction'],
                "probability": decrypted_data['probability'],
                "created_at": prediction.created_at.isoformat()
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting prediction history: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Ошибка при получении истории предсказаний"
        )


@router.get("/history/{prediction_id}")
async def get_prediction_details(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детали конкретного предсказания
    
    Требует авторизации.
    
    - **prediction_id**: ID предсказания
    """
    try:
        # Получаем предсказание
        result = await db.execute(
            select(HeartPrediction)
            .where(
                HeartPrediction.id == prediction_id,
                HeartPrediction.user_id == current_user.id
            )
        )
        
        prediction = result.scalar_one_or_none()
        
        if not prediction:
            raise HTTPException(
                status_code=404,
                detail="Предсказание не найдено"
            )
        
        # Расшифровываем данные
        decrypted_data = encryption_service.decrypt_medical_data({
            'age': prediction.age,
            'sex': prediction.sex,
            'cp': prediction.cp,
            'trestbps': prediction.trestbps,
            'chol': prediction.chol,
            'fbs': prediction.fbs,
            'restecg': prediction.restecg,
            'thalach': prediction.thalach,
            'exang': prediction.exang,
            'oldpeak': prediction.oldpeak,
            'slope': prediction.slope,
            'ca': prediction.ca,
            'thal': prediction.thal,
            'pulse': prediction.pulse,
            'risk_prediction': prediction.risk_prediction,
            'probability': prediction.probability
        })
        
        return {
            "id": prediction.id,
            "age": decrypted_data['age'],
            "sex": decrypted_data['sex'],
            "cp": decrypted_data['cp'],
            "trestbps": decrypted_data['trestbps'],
            "chol": decrypted_data['chol'],
            "fbs": decrypted_data['fbs'],
            "restecg": decrypted_data['restecg'],
            "thalach": decrypted_data['thalach'],
            "exang": decrypted_data['exang'],
            "oldpeak": decrypted_data['oldpeak'],
            "slope": decrypted_data['slope'],
            "ca": decrypted_data['ca'],
            "thal": decrypted_data['thal'],
            "pulse": decrypted_data['pulse'],
            "risk_prediction": decrypted_data['risk_prediction'],
            "probability": decrypted_data['probability'],
            "created_at": prediction.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prediction details: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении деталей предсказания"
        )


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
