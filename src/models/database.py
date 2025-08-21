from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_activated = Column(Boolean, default=False, nullable=False)
    activation_code = Column(String(255), nullable=True)
    activation_code_expires = Column(DateTime, nullable=True)
    activation_attempts = Column(Integer, default=0, nullable=False)
    refresh_token = Column(String(500), nullable=True)  # Добавляем refresh token
    refresh_token_expires = Column(DateTime, nullable=True)  # Время истечения refresh token
    active_chat_id = Column(Integer, ForeignKey("cardio_chats.id"), nullable=True)  # ID активного чата
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    analyses = relationship("CardioAnalysis", back_populates="user")
    active_chat = relationship("CardioChat", foreign_keys=[active_chat_id])


class CardioAnalysis(Base):
    """Модель анализа кардио-ассистента"""
    __tablename__ = "cardio_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    age = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    pulse = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    risk = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    symptoms = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    cached = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Связи
    user = relationship("User", back_populates="analyses")


class HeartPrediction(Base):
    """Модель предсказания сердечных заболеваний"""
    __tablename__ = "heart_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    age = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    sex = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    cp = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    trestbps = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    chol = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    fbs = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    restecg = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    thalach = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    exang = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    oldpeak = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    slope = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    ca = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    thal = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    pulse = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    risk_prediction = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    probability = Column(Text, nullable=False)  # Изменено на Text для зашифрованных данных
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Связи
    user = relationship("User")


class CardioChat(Base):
    __tablename__ = "cardio_chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = Column(JSONB, nullable=False)  # Список сообщений (chat history)
    summary = Column(Text, nullable=True)     # Краткое описание/первые сообщения
    is_active = Column(Boolean, default=True, nullable=False)  # Активен ли чат
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
