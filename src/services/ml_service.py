"""
Сервис для работы с ML моделью
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

class MLService:
    """Сервис для работы с ML моделью предсказания риска"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "data/processed/model.pkl")
        
        self.model_path = model_path
        self.model = None
        self.columns = None
        try:
            self.load_model()
        except Exception as e:
            print(f"⚠️  Предупреждение: Не удалось загрузить модель: {e}")
            print("💡 Запустите: python scripts/train_model.py")
    
    def load_model(self) -> None:
        """Загрузить модель из файла"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Файл модели не найден: {self.model_path}")
            
            artifact = joblib.load(self.model_path)
            self.model = artifact["model"]
            self.columns = artifact["columns"]
            
        except Exception as e:
            raise Exception(f"Ошибка при загрузке модели: {str(e)}")
    
    def predict_heart_risk(self, data: Dict[str, Any]) -> Tuple[int, float]:
        """
        Предсказать риск сердечных заболеваний
        
        Args:
            data: Словарь с данными пациента
            
        Returns:
            Tuple[int, float]: (риск, вероятность)
        """
        try:
            # Создаем DataFrame
            df = pd.DataFrame([data])
            
            # One-hot encoding
            df = pd.get_dummies(df)
            
            # Приводим к нужным колонкам
            df = df.reindex(columns=self.columns, fill_value=0)
            
            # Предсказание
            prediction = self.model.predict(df)[0]
            
            # Вероятность
            if hasattr(self.model, "predict_proba"):
                probability = float(self.model.predict_proba(df)[:, 1][0])
            else:
                probability = float(prediction)
            
            return int(prediction), round(probability, 4)
            
        except Exception as e:
            raise Exception(f"Ошибка при предсказании: {str(e)}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Получить важность признаков
        
        Returns:
            Dict[str, float]: Словарь с важностью признаков
        """
        try:
            if hasattr(self.model, "feature_importances_"):
                importance = self.model.feature_importances_
                feature_importance = dict(zip(self.columns, importance))
                return dict(sorted(feature_importance.items(), 
                                 key=lambda x: x[1], reverse=True))
            else:
                return {}
        except Exception as e:
            raise Exception(f"Ошибка при получении важности признаков: {str(e)}")
    
    def is_healthy(self) -> bool:
        """
        Проверить работоспособность модели
        
        Returns:
            bool: True если модель работает
        """
        try:
            return (self.model is not None and 
                   self.columns is not None and 
                   len(self.columns) > 0)
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Получить информацию о модели
        
        Returns:
            Dict[str, Any]: Информация о модели
        """
        return {
            "model_path": self.model_path,
            "model_type": type(self.model).__name__ if self.model else None,
            "features_count": len(self.columns) if self.columns else 0,
            "is_loaded": self.model is not None,
            "is_healthy": self.is_healthy()
        }
