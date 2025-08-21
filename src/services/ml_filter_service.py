"""
ML-сервис для классификации медицинских вопросов
Использует TF-IDF + Random Forest для определения медицинских вопросов
"""

import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from typing import Tuple, Optional
import re

logger = logging.getLogger(__name__)

class MedicalQuestionClassifier:
    def __init__(self, model_path: str = "data/processed/medical_classifier.pkl"):
        self.model_path = Path(model_path)
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        
    def preprocess_text(self, text: str) -> str:
        """Предобработка текста"""
        if not isinstance(text, str):
            return ""
        
        # Приведение к нижнему регистру
        text = text.lower()
        
        # Удаление специальных символов, оставляем только буквы, цифры и пробелы
        text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', ' ', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def prepare_training_data(self) -> Tuple[list, list]:
        """Подготовка данных для обучения"""
        medical_questions = []
        non_medical_questions = []
        
        # Загружаем данные из нового файла medical_data.csv
        medical_data_path = Path("data/medicalQ/medical_data.csv")
        if medical_data_path.exists():
            df_medical_data = pd.read_csv(medical_data_path)
            logger.info(f"Загружено {len(df_medical_data)} пар вопросов из medical_data.csv")
            
            # Обрабатываем пары вопросов
            for _, row in df_medical_data.iterrows():
                # Вопрос 1 (медицинский)
                if pd.notna(row['question_1']):
                    medical_questions.append(str(row['question_1']))
                
                # Вопрос 2 (может быть медицинским или нет в зависимости от label)
                if pd.notna(row['question_2']):
                    if row['label'] == 1:  # Медицинский
                        medical_questions.append(str(row['question_2']))
                    else:  # Немедицинский
                        non_medical_questions.append(str(row['question_2']))
            
            logger.info(f"Извлечено {len(medical_questions)} медицинских вопросов")
            logger.info(f"Извлечено {len(non_medical_questions)} немедицинских вопросов")
        
        # Дополнительно загружаем старые медицинские вопросы если новый файл не найден
        if not medical_questions:
            medical_path = Path("data/medicalQ/medical_questions.csv")
            if medical_path.exists():
                df_medical = pd.read_csv(medical_path)
                medical_questions = df_medical['question'].tolist()
                logger.info(f"Загружено {len(medical_questions)} медицинских вопросов из старого файла")
        
        # Загружаем дополнительные немедицинские вопросы для баланса
        non_medical_path = Path("data/nonMedicalQ/questions.csv")
        if non_medical_path.exists() and len(non_medical_questions) < 1000:
            df_non_medical = pd.read_csv(non_medical_path)
            # Берем только question1 и question2, исключаем дубликаты
            non_medical_q1 = df_non_medical['question1'].dropna().tolist()
            non_medical_q2 = df_non_medical['question2'].dropna().tolist()
            
            # Добавляем дополнительные немедицинские вопросы для баланса
            additional_non_medical = (non_medical_q1 + non_medical_q2)[:1000]
            non_medical_questions.extend(additional_non_medical)
            logger.info(f"Добавлено {len(additional_non_medical)} дополнительных немедицинских вопросов")
        
        return medical_questions, non_medical_questions
    
    def train_model(self) -> None:
        """Обучение модели"""
        logger.info("Начинаем обучение модели классификации медицинских вопросов...")
        
        # Подготовка данных
        medical_questions, non_medical_questions = self.prepare_training_data()
        
        if not medical_questions or not non_medical_questions:
            logger.error("Недостаточно данных для обучения")
            return
        
        # Создаем датасет
        X = []
        y = []
        
        # Медицинские вопросы (метка 1)
        for question in medical_questions:
            processed = self.preprocess_text(question)
            if processed:
                X.append(processed)
                y.append(1)
        
        # Немедицинские вопросы (метка 0)
        for question in non_medical_questions:
            processed = self.preprocess_text(question)
            if processed:
                X.append(processed)
                y.append(0)
        
        logger.info(f"Всего примеров: {len(X)} (медицинских: {sum(y)}, немедицинских: {len(y) - sum(y)})")
        
        # Разделение на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Создание и обучение TF-IDF векторизатора
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2,
            max_df=0.95
        )
        
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Создание и обучение классификатора
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.classifier.fit(X_train_tfidf, y_train)
        
        # Оценка модели
        y_pred = self.classifier.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Точность модели: {accuracy:.3f}")
        logger.info("Отчет о классификации:")
        logger.info(classification_report(y_test, y_pred))
        
        self.is_trained = True
        
        # Сохранение модели
        self.save_model()
    
    def predict(self, text: str) -> Tuple[bool, float]:
        """
        Предсказание для текста
        Возвращает: (является_медицинским, вероятность)
        """
        if not self.is_trained or not self.vectorizer or not self.classifier:
            logger.warning("Модель не обучена, загружаем сохраненную модель...")
            if not self.load_model():
                logger.error("Не удалось загрузить модель")
                return False, 0.0
        
        # Предобработка текста
        processed_text = self.preprocess_text(text)
        if not processed_text:
            return False, 0.0
        
        # Векторизация
        text_tfidf = self.vectorizer.transform([processed_text])
        
        # Предсказание
        prediction = self.classifier.predict(text_tfidf)[0]
        probability = self.classifier.predict_proba(text_tfidf)[0]
        
        # Возвращаем результат и вероятность медицинского класса
        return bool(prediction), probability[1]
    
    def save_model(self) -> None:
        """Сохранение модели"""
        if not self.is_trained:
            logger.warning("Модель не обучена, сохранение пропущено")
            return
        
        # Создаем директорию если не существует
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'is_trained': self.is_trained
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Модель сохранена в {self.model_path}")
    
    def load_model(self) -> bool:
        """Загрузка модели"""
        if not self.model_path.exists():
            logger.warning(f"Файл модели не найден: {self.model_path}")
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Модель загружена из {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            return False

# Глобальный экземпляр классификатора
classifier = MedicalQuestionClassifier()

def get_medical_classifier() -> MedicalQuestionClassifier:
    """Получение глобального экземпляра классификатора"""
    return classifier
