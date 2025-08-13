"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

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
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    analyses = relationship("CardioAnalysis", back_populates="user")


class CardioAnalysis(Base):
    """Модель анализа кардио-ассистента"""
    __tablename__ = "cardio_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    age = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=False)
    risk = Column(String(50), nullable=False)
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
    age = Column(Integer, nullable=False)
    sex = Column(Integer, nullable=False)
    cp = Column(Integer, nullable=False)
    trestbps = Column(Integer, nullable=False)
    chol = Column(Integer, nullable=False)
    fbs = Column(Integer, nullable=False)
    restecg = Column(Integer, nullable=False)
    thalach = Column(Integer, nullable=False)
    exang = Column(Integer, nullable=False)
    oldpeak = Column(Float, nullable=False)
    slope = Column(Integer, nullable=False)
    ca = Column(Integer, nullable=False)
    thal = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=False)
    risk_prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Связи
    user = relationship("User")
