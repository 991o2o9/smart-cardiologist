from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.schemas import MedicalChatRequest, MedicalChatResponse, MedicalChatMessage
from src.models.database import User, CardioAnalysis, HeartPrediction, CardioChat
from src.services.ai_service import AIService
from src.services.database import get_db
from src.services.encryption_service import encryption_service
from src.utils.auth_middleware import get_current_user
import logging
import datetime
from src.models.schemas import CardioChatSummary, CardioChatDetail, CardioChatMessage as ChatMsgSchema

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

# Utility: check if question is medical (simple filter)
def is_medical_question(messages):
    medical_keywords = [
        # English terms
        'heart', 'cardio', 'pulse', 'pressure', 'blood', 'medicine', 'symptom', 'treatment',
        'cardiologist', 'pain', 'breath', 'hypertension', 'cholesterol', 'risk', 'disease',
        'doctor', 'health', 'diagnosis', 'therapy', 'analysis', 'test', 'ECG', 'blood test',
        'medication', 'recommendation', 'lifestyle', 'exercise', 'diet', 'weight', 'stress',
        'cardiology', 'arrhythmia', 'ischemia', 'myocardial', 'stroke', 'attack', 'artery',
        'vein', 'surgery', 'operation', 'consultation', 'symptoms', 'treatment', 'medications',
        'chest', 'shortness', 'fatigue', 'palpitation', 'fainting', 'swelling', 'blood sugar',
        'diabetes', 'smoking', 'alcohol', 'family history', 'prevention', 'screening',
        # Russian terms
        'сердце', 'кардио', 'пульс', 'давление', 'кровь', 'лекарств', 'симптом', 'лечение',
        'кардиолог', 'боль', 'дыхание', 'гипертони', 'холестерин', 'риск', 'болезн', 'врач',
        'здоровье', 'диагноз', 'терапия', 'анализ', 'тест', 'экг', 'медикамент', 'рекомендац',
        'образ жизни', 'нагрузка', 'диета', 'вес', 'стресс', 'аритмия', 'ишемия', 'инфаркт',
        'инсульт', 'артерия', 'вена', 'операция', 'консультация', 'симптомы', 'грудь',
        'одышка', 'усталость', 'сердцебиение', 'обморок', 'отеки', 'сахар', 'диабет',
        'курение', 'алкоголь', 'наследственность', 'профилактика', 'скрининг',
        # General complaints
        'температура', 'кашель', 'простуда', 'ОРВИ', 'ОРЗ', 'жар', 'головная боль',
        'головокружение', 'тошнота', 'рвота', 'бессонница', 'сон', 'аппетит', 'бессилие',
        'потливость', 'озноб', 'ломота', 'боли в спине', 'боли в ногах', 'боли в руках',
        'тяжесть', 'жжение', 'покалывание', 'покраснение', 'сыпь', 'зуд', 'аллергия',
        'иммунитет', 'температура тела', 'потеря сознания', 'слабость', 'усталость',
        'боли в животе', 'понос', 'запор', 'метеоризм', 'изжога', 'отрыжка', 'рвота',
        'боли в пояснице', 'боли в груди', 'боли при дыхании', 'боли при движении',
        'боли при нагрузке', 'боли после еды', 'боли ночью', 'боли утром', 'боли вечером',
        'боли при ходьбе', 'боли при беге', 'боли при наклоне', 'боли при повороте',
        'боли при кашле', 'боли при чихании', 'боли при глотании', 'боли при разговоре',
        'боли при смехе', 'боли при плаче', 'боли при стрессе', 'боли при волнении',
        'боли при отдыхе', 'боли при работе', 'боли при спорте', 'боли при физической нагрузке'
    ]
    last_user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
    if not last_user_message:
        return False
    return any(word in last_user_message.lower() for word in medical_keywords)

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

@router.post("/", response_model=MedicalChatResponse)
async def medical_chat(
    data: MedicalChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check topic
    if not is_medical_question([m.dict() for m in data.messages]):
        return MedicalChatResponse(response="I can only answer medical questions related to cardiology and health.")

    # 2. Get user profile
    user_profile = get_user_profile(current_user)

    # 3. Get recent analyses and predictions
    analyses, predictions = await get_recent_medical_data(current_user.id, db)

    # 4. Build prompt
    prompt = build_medical_prompt(user_profile, analyses, predictions, [m.dict() for m in data.messages])

    # 5. Get AI response
    try:
        ai_response = ai_service.get_cardio_analysis(
            age=None, pulse=None, risk=None, symptoms=prompt  # prompt instead of symptoms
        )
    except Exception as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # 6. Save chat to CardioChat
    now = datetime.datetime.utcnow().isoformat() + "Z"
    chat_messages = [m.dict() for m in data.messages]
    chat_messages.append({"role": "assistant", "content": ai_response, "timestamp": now})
    summary = chat_messages[0]["content"][:100] if chat_messages else ""
    new_chat = CardioChat(
        user_id=current_user.id,
        messages=chat_messages,
        summary=summary
    )
    db.add(new_chat)
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
