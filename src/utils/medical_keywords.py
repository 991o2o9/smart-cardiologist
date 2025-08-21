"""
Медицинские ключевые слова для быстрого фильтра
Веса: 3 - высокий приоритет, 2 - средний, 1 - низкий
"""

MEDICAL_KEYWORDS = {
    # Высокий приоритет (вес 3) - явные медицинские термины
    'heart': 3, 'cardio': 3, 'cardiovascular': 3, 'cardiology': 3,
    'pulse': 3, 'blood pressure': 3, 'hypertension': 3, 'hypotension': 3,
    'cholesterol': 3, 'triglycerides': 3, 'ECG': 3, 'EKG': 3,
    'arrhythmia': 3, 'atrial fibrillation': 3, 'myocardial': 3,
    'infarction': 3, 'angina': 3, 'pericarditis': 3, 'myocarditis': 3,
    'cardiologist': 3, 'cardiac': 3, 'coronary': 3, 'artery': 3,
    'systolic': 3, 'diastolic': 3, 'beta blocker': 3, 'ACE inhibitor': 3,
    'statin': 3, 'aspirin': 3, 'nitroglycerin': 3, 'warfarin': 3,
    
    # Средний приоритет (вес 2) - симптомы и состояния
    'chest pain': 2, 'chest tightness': 2, 'shortness of breath': 2,
    'palpitations': 2, 'irregular heartbeat': 2, 'heart murmur': 2,
    'dizziness': 2, 'fainting': 2, 'syncope': 2, 'fatigue': 2,
    'swelling': 2, 'edema': 2, 'cough': 2, 'wheezing': 2,
    'nausea': 2, 'vomiting': 2, 'sweating': 2, 'cold sweat': 2,
    'anxiety': 2, 'stress': 2, 'depression': 2, 'insomnia': 2,
    'headache': 2, 'migraine': 2, 'back pain': 2, 'leg pain': 2,
    'arm pain': 2, 'jaw pain': 2, 'shoulder pain': 2,
    'tired': 2, 'trouble sleeping': 2, 'sleeping': 2, 'weight': 2,
    'blood sugar': 2, 'diabetes': 2, 'smoking': 2, 'alcohol': 2,
    'exercise': 2, 'fitness': 2, 'diet': 2, 'lifestyle': 2,
    'lower': 2, 'reduce': 2, 'increase': 2, 'improve': 2,
    'serious': 2, 'dangerous': 2, 'emergency': 2, 'urgent': 2,
    'infection': 2, 'bacterial': 2, 'viral': 2, 'fungal': 2,
    'antibiotic': 2, 'medication': 2, 'prescription': 2, 'dosage': 2,
    'side effect': 2, 'allergic': 2, 'allergy': 2, 'reaction': 2,
    
    # Низкий приоритет (вес 1) - общие медицинские термины
    'doctor': 1, 'physician': 1, 'nurse': 1, 'hospital': 1,
    'clinic': 1, 'emergency': 1, 'ambulance': 1, 'medicine': 1,
    'medication': 1, 'pill': 1, 'tablet': 1, 'injection': 1,
    'treatment': 1, 'therapy': 1, 'diagnosis': 1, 'symptoms': 1,
    'disease': 1, 'condition': 1, 'disorder': 1, 'syndrome': 1,
    'infection': 1, 'inflammation': 1, 'fever': 1, 'temperature': 1,
    'blood test': 1, 'lab test': 1, 'x-ray': 1, 'MRI': 1,
    'CT scan': 1, 'ultrasound': 1, 'biopsy': 1, 'surgery': 1,
    'operation': 1, 'procedure': 1, 'consultation': 1, 'appointment': 1,
    
    # Русские термины - высокий приоритет
    'сердце': 3, 'кардио': 3, 'кардиология': 3, 'кардиолог': 3,
    'пульс': 3, 'давление': 3, 'гипертония': 3, 'гипотония': 3,
    'холестерин': 3, 'экг': 3, 'аритмия': 3, 'инфаркт': 3,
    'стенокардия': 3, 'миокардит': 3, 'перикардит': 3,
    'систолическое': 3, 'диастолическое': 3, 'бета-блокатор': 3,
    
    # Русские термины - средний приоритет
    'боль в груди': 2, 'одышка': 2, 'сердцебиение': 2, 'головокружение': 2,
    'обморок': 2, 'усталость': 2, 'отеки': 2, 'кашель': 2,
    'тошнота': 2, 'рвота': 2, 'потливость': 2, 'стресс': 2,
    'бессонница': 2, 'головная боль': 2, 'мигрень': 2,
    
    # Русские термины - низкий приоритет
    'врач': 1, 'больница': 1, 'клиника': 1, 'скорая': 1,
    'лекарство': 1, 'таблетка': 1, 'лечение': 1, 'диагноз': 1,
    'симптомы': 1, 'болезнь': 1, 'анализ крови': 1, 'операция': 1,
    'консультация': 1, 'прием': 1
}

# Пороги для быстрого фильтра
QUICK_FILTER_THRESHOLD = 0.5  # Минимальный вес для медицинского вопроса
QUICK_FILTER_CONFIDENCE = 0.8  # Уверенность для быстрого ответа

def calculate_medical_score(text: str) -> tuple[float, float]:
    """
    Вычисляет медицинский скор для текста
    Возвращает: (общий вес, уверенность)
    """
    text_lower = text.lower()
    total_weight = 0
    word_count = 0
    
    for keyword, weight in MEDICAL_KEYWORDS.items():
        if keyword in text_lower:
            total_weight += weight
            word_count += 1
    
    # Нормализуем по длине текста
    text_length = len(text.split())
    if text_length > 0:
        normalized_score = total_weight / text_length
    else:
        normalized_score = 0
    
    # Вычисляем уверенность
    confidence = min(1.0, normalized_score / 0.5)  # 0.5 - максимальный ожидаемый скор
    
    return normalized_score, confidence

def quick_medical_filter(text: str) -> tuple[bool, float]:
    """
    Быстрый фильтр на основе ключевых слов
    Возвращает: (является_медицинским, уверенность)
    """
    score, confidence = calculate_medical_score(text)
    
    is_medical = score >= QUICK_FILTER_THRESHOLD
    return is_medical, confidence
