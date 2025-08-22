from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.schemas import MedicalChatRequest, MedicalChatResponse, MedicalChatMessage
from models.database import User, CardioAnalysis, HeartPrediction, CardioChat
from services.ai_service import AIService
from services.database import get_db
from services.encryption_service import encryption_service
from utils.auth_middleware import get_current_user
from services.three_level_filter import get_medical_filter
import logging
import datetime
from models.schemas import CardioChatSummary, CardioChatDetail, CardioChatMessage as ChatMsgSchema, ActiveChatResponse, CreateChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cardio-assistant", tags=["Cardio Assistant"])
ai_service = AIService()

# Utility: get user profile (expand as needed)
def get_user_profile(user: User):
    return {
        "email": user.email,
        # add more fields if needed
    }

# Utility: get last N analyses and predictions
async def get_recent_medical_data(user_id, db, n=3):
    # CardioAnalysis
    analyses = []
    result = await db.execute(
        select(CardioAnalysis)
        .where(CardioAnalysis.user_id == user_id)
        .order_by(CardioAnalysis.created_at.desc())
        .limit(n)
    )
    for a in result.scalars().all():
        decrypted = encryption_service.decrypt_medical_data({
            'age': a.age,
            'pulse': a.pulse,
            'risk': a.risk,
            'symptoms': a.symptoms
        })
        analyses.append(decrypted)
    # HeartPrediction
    predictions = []
    result2 = await db.execute(
        select(HeartPrediction)
        .where(HeartPrediction.user_id == user_id)
        .order_by(HeartPrediction.created_at.desc())
        .limit(n)
    )
    for p in result2.scalars().all():
        decrypted = encryption_service.decrypt_medical_data({
            'age': p.age,
            'sex': p.sex,
            'cp': p.cp,
            'trestbps': p.trestbps,
            'chol': p.chol,
            'fbs': p.fbs,
            'restecg': p.restecg,
            'thalach': p.thalach,
            'exang': p.exang,
            'oldpeak': p.oldpeak,
            'slope': p.slope,
            'ca': p.ca,
            'thal': p.thal,
            'pulse': p.pulse,
            'risk_prediction': p.risk_prediction,
            'probability': p.probability
        })
        predictions.append(decrypted)
    return analyses, predictions

# Utility: check if question is medical using three-level filter
def is_medical_question(messages):
    """Проверка медицинского вопроса с использованием трёхуровневой системы фильтрации"""
    last_user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
    if not last_user_message:
        return False
    
    # Используем трёхуровневую систему фильтрации
    medical_filter = get_medical_filter()
    filter_result = medical_filter.filter_question(last_user_message)
    
    # Логируем результат фильтрации
    logger.info(f"Фильтрация вопроса: '{last_user_message[:50]}...' -> {filter_result['method']} (медицинский: {filter_result['is_medical']}, уверенность: {filter_result['confidence']:.3f})")
    
    return filter_result['is_medical']

# Utility: build prompt for AI
def build_medical_prompt(user_profile, analyses, predictions, messages):
    prompt = (
        "You are an experienced cardiologist. Answer only medical questions related to cardiology, heart health, lifestyle, medications, and test results. "
        "Do not answer non-medical questions. If the question is not about medicine, politely refuse to answer.\n\n"
        f"User profile: {user_profile}\n"
        f"Recent analyses: {analyses}\n"
        f"Recent predictions: {predictions}\n"
        f"Chat history: {messages}\n"
        "Give a detailed, clear, and personalized answer. If needed, recommend seeing a doctor in person."
    )
    return prompt

# Utility: get or create active chat for user
async def get_or_create_active_chat(user: User, db: AsyncSession):
    """Получить активный чат пользователя или создать новый"""
    # Проверяем есть ли активный чат
    if user.active_chat_id:
        result = await db.execute(
            select(CardioChat)
            .where(CardioChat.id == user.active_chat_id, CardioChat.user_id == user.id, CardioChat.is_active == True)
        )
        active_chat = result.scalar_one_or_none()
        if active_chat:
            return active_chat
    
    # Если активного чата нет, создаем новый
    new_chat = CardioChat(
        user_id=user.id,
        messages=[],
        summary="",
        is_active=True
    )
    db.add(new_chat)
    await db.flush()  # Получаем ID нового чата
    
    # Обновляем активный чат у пользователя
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(active_chat_id=new_chat.id)
    )
    
    await db.commit()
    return new_chat

# Utility: deactivate other chats for user
async def deactivate_other_chats(user_id: int, current_chat_id: int, db: AsyncSession):
    """Деактивировать все остальные чаты пользователя"""
    await db.execute(
        update(CardioChat)
        .where(CardioChat.user_id == user_id, CardioChat.id != current_chat_id, CardioChat.is_active == True)
        .values(is_active=False)
    )

@router.get("/active", response_model=ActiveChatResponse)
async def get_active_chat(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить активный чат пользователя"""
    active_chat = await get_or_create_active_chat(current_user, db)
    
    messages = [ChatMsgSchema(**msg) for msg in active_chat.messages]
    return ActiveChatResponse(
        chat_id=active_chat.id,
        messages=messages,
        summary=active_chat.summary,
        created_at=active_chat.created_at.isoformat() + "Z",
        updated_at=active_chat.updated_at.isoformat() + "Z"
    )

@router.post("/create", response_model=CreateChatResponse)
async def create_new_chat(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый чат"""
    # Деактивируем текущий активный чат
    if current_user.active_chat_id:
        await db.execute(
            update(CardioChat)
            .where(CardioChat.id == current_user.active_chat_id)
            .values(is_active=False)
        )
    
    # Создаем новый чат
    new_chat = CardioChat(
        user_id=current_user.id,
        messages=[],
        summary="",
        is_active=True
    )
    db.add(new_chat)
    await db.flush()
    
    # Обновляем активный чат у пользователя
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(active_chat_id=new_chat.id)
    )
    
    await db.commit()
    
    return CreateChatResponse(chat_id=new_chat.id)

@router.post("/", response_model=MedicalChatResponse)
async def medical_chat(
    data: MedicalChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check topic
    if not is_medical_question([m.dict() for m in data.messages]):
        return MedicalChatResponse(response="I can only answer medical questions related to cardiology and health.")

    # 2. Get or create active chat
    active_chat = await get_or_create_active_chat(current_user, db)

    # 3. Get user profile
    user_profile = get_user_profile(current_user)

    # 4. Get recent analyses and predictions
    analyses, predictions = await get_recent_medical_data(current_user.id, db)

    # 5. Build prompt with chat history
    all_messages = active_chat.messages + [m.dict() for m in data.messages]
    prompt = build_medical_prompt(user_profile, analyses, predictions, all_messages)

    # 6. Get AI response
    try:
        ai_response = ai_service.get_cardio_analysis(
            age=None, pulse=None, risk=None, symptoms=prompt  # prompt instead of symptoms
        )
    except Exception as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # 7. Add messages to chat
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Добавляем сообщения пользователя
    for message in data.messages:
        active_chat.messages.append({
            "role": message.role,
            "content": message.content,
            "timestamp": now
        })
    
    # Добавляем ответ ИИ
    active_chat.messages.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": now
    })
    
    # Обновляем summary
    if not active_chat.summary and data.messages:
        active_chat.summary = data.messages[0].content[:100]
    
    # Обновляем время
    active_chat.updated_at = datetime.datetime.utcnow()
    
    await db.commit()
    
    return MedicalChatResponse(response=ai_response)

@router.get("/history", response_model=list[CardioChatSummary])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    result = await db.execute(
        select(CardioChat)
        .where(CardioChat.user_id == current_user.id)
        .order_by(CardioChat.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    chats = result.scalars().all()
    return [
        CardioChatSummary(
            id=chat.id,
            summary=chat.summary,
            created_at=chat.created_at.isoformat() + "Z",
            updated_at=chat.updated_at.isoformat() + "Z"
        ) for chat in chats
    ]

@router.get("/history/{chat_id}", response_model=CardioChatDetail)
async def get_chat_detail(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CardioChat)
        .where(CardioChat.id == chat_id, CardioChat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = [ChatMsgSchema(**msg) for msg in chat.messages]
    return CardioChatDetail(
        id=chat.id,
        messages=messages,
        summary=chat.summary,
        created_at=chat.created_at.isoformat() + "Z",
        updated_at=chat.updated_at.isoformat() + "Z"
    )

@router.post("/history/{chat_id}/activate")
async def activate_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Активировать конкретный чат"""
    # Проверяем что чат принадлежит пользователю
    result = await db.execute(
        select(CardioChat)
        .where(CardioChat.id == chat_id, CardioChat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Деактивируем все остальные чаты
    await deactivate_other_chats(current_user.id, chat_id, db)
    
    # Активируем выбранный чат
    await db.execute(
        update(CardioChat)
        .where(CardioChat.id == chat_id)
        .values(is_active=True)
    )
    
    # Обновляем активный чат у пользователя
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(active_chat_id=chat_id)
    )
    
    await db.commit()
    
    return {"message": "Chat activated successfully"}
