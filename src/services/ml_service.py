import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from config.settings import settings

load_dotenv()

class MLService:
    """Service for working with ML risk prediction model"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = settings.MODEL_PATH
        
        self.model_path = model_path
        self.model = None
        self.columns = None
        try:
            self.load_model()
        except Exception as e:
            print(f"⚠️  Warning: Failed to load model: {e}")
            print("💡 Run: python scripts/train_model.py")
    
    def load_model(self) -> None:
        """Load model from file"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            artifact = joblib.load(self.model_path)
            self.model = artifact["model"]
            self.columns = artifact["columns"]
            
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def predict_heart_risk(self, data: Dict[str, Any]) -> Tuple[int, float]:
        """
        Predict heart disease risk
        
        Args:
            data: Dictionary with patient data
            
        Returns:
            Tuple[int, float]: (risk, probability)
        """
        try:
            # Create DataFrame
            df = pd.DataFrame([data])
            
            # One-hot encoding
            df = pd.get_dummies(df)
            
            # Align with required columns
            df = df.reindex(columns=self.columns, fill_value=0)
            
            # Prediction
            prediction = self.model.predict(df)[0]
            
            # Probability
            if hasattr(self.model, "predict_proba"):
                probability = float(self.model.predict_proba(df)[:, 1][0])
            else:
                probability = float(prediction)
            
            return int(prediction), round(probability, 4)
            
        except Exception as e:
            raise Exception(f"Error during prediction: {str(e)}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance
        
        Returns:
            Dict[str, float]: Dictionary with feature importance
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
            raise Exception(f"Error getting feature importance: {str(e)}")
    
    def is_healthy(self) -> bool:
        """
        Check model health
        
        Returns:
            bool: True if model is working
        """
        try:
            return (self.model is not None and 
                   self.columns is not None and 
                   len(self.columns) > 0)
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "model_path": self.model_path,
            "model_type": type(self.model).__name__ if self.model else None,
            "features_count": len(self.columns) if self.columns else 0,
            "is_loaded": self.model is not None,
            "is_healthy": self.is_healthy()
        }
