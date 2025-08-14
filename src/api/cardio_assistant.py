from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.schemas import CardioRequest, CardioResponse
from src.models.database import User, CardioAnalysis
from src.services.ai_service import AIService
from src.services.database import get_db
from src.services.encryption_service import encryption_service
from src.utils.cache import cache
from src.utils.rate_limiter import rate_limiter
from src.utils.auth_middleware import get_current_user
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cardio-assistant", tags=["Cardio Assistant"])

# Инициализация сервисов
ai_service = AIService()


def create_cache_key(data: dict) -> str:
    """Создать ключ кеша из данных запроса"""
    # Сортируем ключи для консистентности
    sorted_data = dict(sorted(data.items()))
    data_str = json.dumps(sorted_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


@router.post("/", response_model=CardioResponse)
async def get_cardio_analysis(
    request: CardioRequest, 
    req: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить анализ от AI кардиолога
    
    Требует авторизации.
    
    - **age**: Возраст пациента (0-120)
    - **pulse**: Пульс в минуту (40-200)
    - **risk**: Уровень риска (низкий/средний/высокий)
    - **symptoms**: Описание симптомов
    """
    ip = req.client.host
    
    # Проверка rate limiting
    if not rate_limiter.is_allowed(ip):
        raise HTTPException(
            status_code=429, 
            detail="Слишком много запросов. Попробуйте позже."
        )
    
    # Создаем ключ кеша
    cache_key = create_cache_key(request.model_dump())
    
    # Проверяем кеш
    cached_response = cache.get(cache_key)
    if cached_response:
        # Шифруем данные перед сохранением
        encrypted_data = encryption_service.encrypt_medical_data({
            'age': request.age,
            'pulse': request.pulse,
            'risk': request.risk,
            'symptoms': request.symptoms,
            'ai_response': cached_response
        })
        
        # Сохраняем в базу данных как кешированный ответ
        analysis = CardioAnalysis(
            user_id=current_user.id,
            age=encrypted_data['age'],
            pulse=encrypted_data['pulse'],
            risk=encrypted_data['risk'],
            symptoms=encrypted_data['symptoms'],
            ai_response=encrypted_data['ai_response'],
            cached=True
        )
        db.add(analysis)
        await db.commit()
        
        return CardioResponse(cached=True, response=cached_response)
    
    try:
        # Получаем анализ от AI
        ai_response = ai_service.get_cardio_analysis(
            age=request.age,
            pulse=request.pulse,
            risk=request.risk,
            symptoms=request.symptoms
        )
        
        # Сохраняем в кеш
        cache.set(cache_key, ai_response)
        
        # Шифруем данные перед сохранением
        encrypted_data = encryption_service.encrypt_medical_data({
            'age': request.age,
            'pulse': request.pulse,
            'risk': request.risk,
            'symptoms': request.symptoms,
            'ai_response': ai_response
        })
        
        # Сохраняем в базу данных
        analysis = CardioAnalysis(
            user_id=current_user.id,
            age=encrypted_data['age'],
            pulse=encrypted_data['pulse'],
            risk=encrypted_data['risk'],
            symptoms=encrypted_data['symptoms'],
            ai_response=encrypted_data['ai_response'],
            cached=False
        )
        db.add(analysis)
        await db.commit()
        
        logger.info(f"Cardio analysis saved for user {current_user.id}")
        
        return CardioResponse(cached=False, response=ai_response)
        
    except Exception as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка AI сервиса: {str(e)}")


@router.get("/history", response_model=list[dict])
async def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Получить историю анализов пользователя
    
    Требует авторизации.
    
    - **limit**: Количество записей (по умолчанию 10)
    - **offset**: Смещение (по умолчанию 0)
    """
    try:
        # Получаем историю анализов
        result = await db.execute(
            select(CardioAnalysis)
            .where(CardioAnalysis.user_id == current_user.id)
            .order_by(CardioAnalysis.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        analyses = result.scalars().all()
        
        # Формируем ответ с расшифровкой данных
        history = []
        for analysis in analyses:
            # Расшифровываем данные
            decrypted_data = encryption_service.decrypt_medical_data({
                'age': analysis.age,
                'pulse': analysis.pulse,
                'risk': analysis.risk,
                'symptoms': analysis.symptoms
            })
            
            history.append({
                "id": analysis.id,
                "age": decrypted_data['age'],
                "pulse": decrypted_data['pulse'],
                "risk": decrypted_data['risk'],
                "symptoms": decrypted_data['symptoms'],
                "cached": analysis.cached,
                "created_at": analysis.created_at.isoformat()
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Ошибка при получении истории анализов"
        )


@router.get("/history/{analysis_id}")
async def get_analysis_details(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детали конкретного анализа
    
    Требует авторизации.
    
    - **analysis_id**: ID анализа
    """
    try:
        # Получаем анализ
        result = await db.execute(
            select(CardioAnalysis)
            .where(
                CardioAnalysis.id == analysis_id,
                CardioAnalysis.user_id == current_user.id
            )
        )
        
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Анализ не найден"
            )
        
        # Расшифровываем данные
        decrypted_data = encryption_service.decrypt_medical_data({
            'age': analysis.age,
            'pulse': analysis.pulse,
            'risk': analysis.risk,
            'symptoms': analysis.symptoms,
            'ai_response': analysis.ai_response
        })
        
        return {
            "id": analysis.id,
            "age": decrypted_data['age'],
            "pulse": decrypted_data['pulse'],
            "risk": decrypted_data['risk'],
            "symptoms": decrypted_data['symptoms'],
            "ai_response": decrypted_data['ai_response'],
            "cached": analysis.cached,
            "created_at": analysis.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis details: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении деталей анализа"
        )


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "ai_service": ai_service.is_healthy(),
        "cache_stats": cache.get_stats(),
        "rate_limiter_stats": rate_limiter.get_stats()
    }
