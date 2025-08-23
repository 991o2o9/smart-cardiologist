from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models.schemas import MedicalChatRequest, MedicalChatResponse, MedicalChatMessage
from src.models.database import User, CardioAnalysis, HeartPrediction, CardioChat
from src.services.ai_service import AIService
from src.services.database import get_db
from src.services.encryption_service import encryption_service
from src.utils.auth_middleware import get_current_user
from src.services.three_level_filter import get_medical_filter
import logging
import datetime
from src.models.schemas import CardioChatSummary, CardioChatDetail, CardioChatMessage as ChatMsgSchema, ActiveChatResponse, CreateChatResponse, DeleteChatResponse, DeleteAllChatsResponse

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

# Utility: analyze medical context of conversation
def analyze_medical_context(messages):
    """Анализирует медицинский контекст всей беседы"""
    if not messages:
        return False, 0.0
    
    # Счетчики для анализа
    medical_messages = 0
    total_user_messages = 0
    
    # Медицинские ключевые слова (расширенный список)
    medical_keywords = [
        # Русские медицинские термины
        'сердце', 'кардиолог', 'давление', 'пульс', 'холестерин', 'аритмия', 'инфаркт', 'стенокардия',
        'здоровье', 'болезнь', 'симптом', 'боль', 'лечение', 'лекарство', 'таблетка', 'врач',
        'кровь', 'сосуды', 'артерии', 'вены', 'гипертония', 'гипотония', 'диабет', 'ожирение',
        'курение', 'алкоголь', 'спорт', 'физическая активность', 'диета', 'питание', 'сон', 'стресс',
        'электрокардиограмма', 'экг', 'узи', 'анализ', 'результат', 'норма', 'отклонение',
        
        # Английские медицинские термины
        'heart', 'cardio', 'blood pressure', 'pulse', 'cholesterol', 'arrhythmia', 'heart attack', 'angina',
        'health', 'disease', 'symptom', 'pain', 'treatment', 'medicine', 'pill', 'doctor',
        'blood', 'vessels', 'arteries', 'veins', 'hypertension', 'hypotension', 'diabetes', 'obesity',
        'smoking', 'alcohol', 'exercise', 'physical activity', 'diet', 'nutrition', 'sleep', 'stress',
        'electrocardiogram', 'ecg', 'ultrasound', 'test', 'result', 'normal', 'abnormal'
    ]
    
    # Анализируем каждое сообщение пользователя
    for msg in messages:
        if msg['role'] == 'user':
            total_user_messages += 1
            content_lower = msg['content'].lower()
            
            # Проверяем наличие медицинских ключевых слов
            if any(keyword in content_lower for keyword in medical_keywords):
                medical_messages += 1
    
    # Вычисляем процент медицинских сообщений
    if total_user_messages == 0:
        return False, 0.0
    
    medical_ratio = medical_messages / total_user_messages
    
    # Определяем медицинский контекст
    is_medical = medical_ratio >= 0.3  # Если 30% или больше сообщений медицинские
    
    logger.info(f"Анализ контекста: {medical_messages}/{total_user_messages} медицинских сообщений (соотношение: {medical_ratio:.2f})")
    
    return is_medical, medical_ratio

# Utility: check if question is medical using three-level filter
def is_medical_question(messages):
    """Проверка медицинского вопроса с использованием трёхуровневой системы фильтрации"""
    if not messages:
        return False
    
    # Если это первое сообщение в чате - проверяем его на медицинскую тематику
    if len(messages) == 1:
        last_user_message = messages[0]['content']
        medical_filter = get_medical_filter()
        filter_result = medical_filter.filter_question(last_user_message)
        
        logger.info(f"Фильтрация первого вопроса: '{last_user_message[:50]}...' -> {filter_result['method']} (медицинский: {filter_result['is_medical']}, уверенность: {filter_result['confidence']:.3f})")
        return filter_result['is_medical']
    
    # Если это продолжение беседы - анализируем контекст
    context_is_medical, context_confidence = analyze_medical_context(messages)
    
    # Если контекст медицинский, разрешаем продолжение
    if context_is_medical:
        logger.info(f"В контексте беседы обнаружен медицинский контекст (уверенность: {context_confidence:.2f}) - разрешаем продолжение")
        return True
    
    # Если контекст не медицинский, проверяем последнее сообщение
    last_user_message = messages[-1]['content']
    medical_filter = get_medical_filter()
    filter_result = medical_filter.filter_question(last_user_message)
    
    logger.info(f"Фильтрация вопроса в не-медицинском контексте: '{last_user_message[:50]}...' -> {filter_result['method']} (медицинский: {filter_result['is_medical']}, уверенность: {filter_result['confidence']:.3f})")
    return filter_result['is_medical']

# Utility: build prompt for AI
def build_medical_prompt(user_profile, analyses, predictions, messages):
    # Определяем тип вопроса и контекст
    if len(messages) == 1:
        question_type = "первичный медицинский вопрос"
        context_instruction = "This is the first question in the conversation. Provide a comprehensive medical answer."
    else:
        question_type = "уточняющий вопрос или продолжение медицинской беседы"
        # Анализируем контекст для лучших инструкций
        context_is_medical, context_confidence = analyze_medical_context(messages)
        if context_is_medical:
            context_instruction = f"This is a follow-up question in a medical conversation (medical context confidence: {context_confidence:.2f}). Continue providing medical advice based on the conversation context."
        else:
            context_instruction = "This appears to be a follow-up question. Please ensure it's related to the medical discussion before answering."
    
    # Получаем последние сообщения для контекста
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    prompt = (
        f"You are an experienced cardiologist. The user is asking a {question_type}.\n\n"
        f"CONTEXT: {context_instruction}\n\n"
        "IMPORTANT: You can answer:\n"
        "- Medical questions related to cardiology, heart health, lifestyle, medications, and test results\n"
        "- Follow-up questions that continue the medical discussion (like 'explain more', 'what else', 'how to improve')\n"
        "- Clarification requests about your previous medical advice\n"
        "- Questions about implementing your medical recommendations\n\n"
        "Do NOT answer:\n"
        "- Completely unrelated non-medical questions\n"
        "- Questions about politics, entertainment, or other non-health topics\n\n"
        f"User profile: {user_profile}\n"
        f"Recent medical analyses: {analyses}\n"
        f"Recent heart predictions: {predictions}\n"
        f"Chat history (last 10 messages): {recent_messages}\n\n"
        "Give a detailed, clear, and personalized medical answer. If needed, recommend seeing a doctor in person. "
        "If this is a follow-up question, provide additional details or clarification based on the medical context. "
        "Always maintain the medical focus of the conversation."
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
    
    # Если активного чата нет, создаем новый БЕЗ сообщений
    new_chat = CardioChat(
        user_id=user.id,
        messages=[],
        summary="",  # Пустой summary - будет заполнен первым сообщением пользователя
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
    
    # Если чат пустой (нет сообщений), возвращаем пустой чат
    if not active_chat.messages:
        logger.info(f"Активный чат {active_chat.id} пустой - ожидается первое сообщение пользователя")
    
    messages = [ChatMsgSchema(**msg) for msg in active_chat.messages]
    return ActiveChatResponse(
        chat_id=active_chat.id,
        messages=messages,
        summary=active_chat.summary or "",  # Если summary пустой, возвращаем пустую строку
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
    
    # Создаем новый чат БЕЗ сообщений
    new_chat = CardioChat(
        user_id=current_user.id,
        messages=[],
        summary="",  # Пустой summary - будет заполнен первым сообщением пользователя
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
    logger.info(f"Получен запрос на медицинский чат от пользователя {current_user.id}")
    
    # 1. Get or create active chat first
    active_chat = await get_or_create_active_chat(current_user, db)
    logger.info(f"Активный чат: {active_chat.id}, сообщений в истории: {len(active_chat.messages)}")

    # 2. Build complete message history for context analysis
    all_messages = active_chat.messages + [m.dict() for m in data.messages]
    logger.info(f"Общее количество сообщений для анализа: {len(all_messages)}")
    
    # 3. Check if question is medical using context
    is_medical = is_medical_question(all_messages)
    logger.info(f"Результат проверки медицинского вопроса: {is_medical}")
    
    if not is_medical:
        logger.warning(f"Вопрос не прошел медицинскую фильтрацию для пользователя {current_user.id}")
        return MedicalChatResponse(response="I can only answer medical questions related to cardiology and health.")

    # 4. Get user profile
    user_profile = get_user_profile(current_user)

    # 5. Get recent analyses and predictions
    analyses, predictions = await get_recent_medical_data(current_user.id, db)
    logger.info(f"Получено анализов: {len(analyses)}, предсказаний: {len(predictions)}")

    # 6. Build prompt with chat history
    prompt = build_medical_prompt(user_profile, analyses, predictions, all_messages)
    logger.info(f"Построен промпт для ИИ длиной {len(prompt)} символов")

    # 7. Get AI response
    try:
        logger.info("Отправка запроса к ИИ...")
        
        # Получаем последнее сообщение пользователя для анализа
        last_user_message = data.messages[-1].content if data.messages else ""
        
        # Подготавливаем историю диалога для контекста
        conversation_history = []
        
        # Добавляем последние сообщения из истории чата (если есть)
        if active_chat.messages:
            # Берем последние 5 сообщений из истории
            recent_history = active_chat.messages[-5:]
            conversation_history.extend(recent_history)
        
        # Добавляем текущие сообщения пользователя
        for message in data.messages:
            conversation_history.append({
                "role": message.role,
                "content": message.content
            })
        
        logger.info(f"Подготовлена история диалога: {len(conversation_history)} сообщений")
        
        # Используем адаптивный ответ с контекстом
        ai_response = ai_service.get_adaptive_response(last_user_message, conversation_history)
        logger.info(f"Получен адаптивный ответ от ИИ длиной {len(ai_response)} символов")
        
        # Дополнительная проверка ответа
        if ai_response and len(ai_response.strip()) > 0:
            logger.info(f"Ответ успешно получен. Первые 100 символов: {ai_response[:100]}...")
            logger.info(f"Последние 100 символов: ...{ai_response[-100:]}")
        else:
            logger.warning("Получен пустой ответ от ИИ")
            
    except Exception as e:
        logger.error(f"Ошибка ИИ сервиса: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # 8. Add messages to chat
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
    
    # Обновляем summary - берем первое сообщение пользователя в чате
    if not active_chat.summary and data.messages:
        # Если это первое сообщение в чате, используем его как summary
        first_user_message = data.messages[0].content
        active_chat.summary = first_user_message[:100] + ("..." if len(first_user_message) > 100 else "")
        logger.info(f"Установлен summary чата: '{active_chat.summary}'")
    
    # Обновляем время
    active_chat.updated_at = datetime.datetime.utcnow()
    
    # Явно уведомляем SQLAlchemy об изменениях в JSONB поле
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(active_chat, "messages")
    
    await db.commit()
    logger.info(f"Чат обновлен, всего сообщений: {len(active_chat.messages)}")
    
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

@router.delete("/history/{chat_id}", response_model=DeleteChatResponse)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить конкретный чат"""
    # Проверяем что чат принадлежит пользователю
    result = await db.execute(
        select(CardioChat)
        .where(CardioChat.id == chat_id, CardioChat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Проверяем, не является ли это активным чатом
    if chat.is_active:
        raise HTTPException(status_code=400, detail="Cannot delete active chat. Please activate another chat first.")
    
    # Удаляем чат
    await db.delete(chat)
    await db.commit()
    
    return DeleteChatResponse(message="Чат успешно удален")

@router.delete("/history", response_model=DeleteAllChatsResponse)
async def delete_all_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить всю историю чатов пользователя"""
    # Получаем все чаты пользователя
    result = await db.execute(
        select(CardioChat)
        .where(CardioChat.user_id == current_user.id)
    )
    chats = result.scalars().all()
    
    if not chats:
        return DeleteAllChatsResponse(message="История чатов пуста", deleted_count=0)
    
    # Подсчитываем количество чатов для удаления (исключая активный)
    chats_to_delete = [chat for chat in chats if not chat.is_active]
    deleted_count = len(chats_to_delete)
    
    # Удаляем неактивные чаты
    for chat in chats_to_delete:
        await db.delete(chat)
    
    # Если есть активный чат, очищаем его сообщения и обновляем summary
    active_chat = next((chat for chat in chats if chat.is_active), None)
    if active_chat:
        active_chat.messages = []
        active_chat.summary = ""  # Пустой summary - будет заполнен следующим сообщением пользователя
        active_chat.updated_at = datetime.datetime.utcnow()
        # Явно уведомляем SQLAlchemy об изменениях в JSONB поле
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(active_chat, "messages")
    
    await db.commit()
    
    return DeleteAllChatsResponse(
        message="Вся история чатов успешно удалена",
        deleted_count=deleted_count
    )
