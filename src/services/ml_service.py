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
        self.scaler = None
        self.feature_means: Dict[str, Any] = {}
        try:
            self.load_model()
        except Exception as e:
            print(f"⚠️  Warning: Failed to load model: {e}")
            print("💡 Run: python scripts/train_model.py")
        # Try to pre-load feature means, but don't fail if file is missing
        try:
            self._load_feature_means()
        except Exception:
            # Will compute lazily on first use
            pass
    
    def load_model(self) -> None:
        """Load model from file"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            artifact = joblib.load(self.model_path)
            self.model = artifact["model"]
            self.columns = artifact["columns"]
            
            # Load scaler if available
            if "scaler" in artifact:
                self.scaler = artifact["scaler"]
            else:
                self.scaler = None
                print("⚠️  Warning: No scaler found in model artifact")
            
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def _load_feature_means(self) -> None:
        """Load dataset and compute feature means for imputation.
        Uses the same dataset path as training script.
        """
        # Default training data path
        data_path = os.path.join("data", "raw", "heart.xls")
        if not os.path.exists(data_path):
            # Try .xlsx fallback
            data_path_xlsx = os.path.join("data", "raw", "heart.xlsx")
            if os.path.exists(data_path_xlsx):
                data_path = data_path_xlsx
            else:
                raise FileNotFoundError("Training dataset not found for computing feature means.")
        # Read dataset (Excel or CSV)
        try:
            if data_path.endswith(".xls"):
                # xlrd is required for .xls
                df = pd.read_excel(data_path, engine="xlrd")
            elif data_path.endswith(".xlsx"):
                df = pd.read_excel(data_path, engine="openpyxl")
            else:
                df = pd.read_csv(data_path)
        except Exception:
            # Fallback: if reading fails for any reason, use empty DataFrame to rely on defaults
            df = pd.DataFrame()
        # Remove rows with target missing if present
        if "target" in df.columns:
            df = df.dropna(subset=["target"])  # keep target but exclude NaN rows
        # Expected input fields
        expected_fields = [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal", "pulse"
        ]
        # Some datasets may not include pulse; handle gracefully
        means: Dict[str, Any] = {}
        for field in expected_fields:
            if field in df.columns:
                # For numeric columns, compute mean
                value = df[field].astype(float).mean()
                # Integer-coded fields should be rounded to nearest int
                if field in {"sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal", "pulse", "trestbps", "chol", "thalach", "age"}:
                    # round and cast to int, guard NaN
                    value = int(round(value)) if pd.notna(value) else 0
                else:
                    value = float(value) if pd.notna(value) else 0.0
                means[field] = value
        # Defaults if some fields were absent
        defaults = {
            "age": 54,
            "sex": 1,
            "cp": 0,
            "trestbps": 130,
            "chol": 246,
            "fbs": 0,
            "restecg": 0,
            "thalach": 149,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 1,
            "ca": 0,
            "thal": 2,
            "pulse": 80,
        }
        for k, v in defaults.items():
            means.setdefault(k, v)
        self.feature_means = means
    
    def get_feature_means(self) -> Dict[str, Any]:
        """Return cached feature means, computing if necessary."""
        if not self.feature_means:
            self._load_feature_means()
        return self.feature_means
    
    def fill_missing_with_means(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing input fields with dataset means.
        Does not modify provided fields.
        """
        means = self.get_feature_means()
        filled = dict(data) if data is not None else {}
        # Ensure all 15 fields present
        for field, mean_value in means.items():
            if field not in filled or filled[field] is None:
                filled[field] = mean_value
        return filled
    
    def predict_heart_risk(self, data: Dict[str, Any]) -> Tuple[int, float]:
        """
        Predict heart disease risk
        
        Args:
            data: Dictionary with patient data
            
        Returns:
            Tuple[int, float]: (risk, probability)
        """
        try:
            # Create DataFrame with correct order of features
            df = pd.DataFrame([data])
            
            # Ensure all required columns are present in the same order as training
            # The model expects the original 14 features, not one-hot encoded
            expected_features = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'pulse'
            ]
            
            # Reorder columns to match training data
            df = df.reindex(columns=expected_features, fill_value=0)
            
            # Apply the same preprocessing as during training
            # One-hot encoding for categorical variables
            categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
            df_encoded = pd.get_dummies(df, columns=categorical_cols)
            
            # Align with required columns from training
            df_encoded = df_encoded.reindex(columns=self.columns, fill_value=0)
            
            # Apply scaling if scaler is available
            if hasattr(self, 'scaler') and self.scaler is not None:
                df_scaled = self.scaler.transform(df_encoded)
            else:
                df_scaled = df_encoded.values
            
            # Prediction
            prediction = self.model.predict(df_scaled)[0]
            
            # Probability
            if hasattr(self.model, "predict_proba"):
                probability = float(self.model.predict_proba(df_scaled)[:, 1][0])
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
            "has_scaler": self.scaler is not None,
            "is_healthy": self.is_healthy()
        }
