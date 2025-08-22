#!/usr/bin/env python3
"""
Script for training heart disease risk prediction model
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(data_path: str) -> pd.DataFrame:
    """Load training data"""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load data
    if data_path.endswith('.xls'):
        data = pd.read_excel(data_path, engine='xlrd')
    elif data_path.endswith('.xlsx'):
        data = pd.read_excel(data_path, engine='openpyxl')
    elif data_path.endswith('.csv'):
        data = pd.read_csv(data_path)
    else:
        raise ValueError("Unsupported file format. Use .xls, .xlsx, or .csv")
    
    logger.info(f"Data loaded: {data.shape}")
    return data

def preprocess_data(data: pd.DataFrame) -> tuple:
    """Preprocess data for training"""
    # Remove duplicates
    data = data.drop_duplicates()
    
    # Handle missing values
    data = data.dropna()
    
    # Separate features and target
    X = data.drop('target', axis=1)
    y = data['target']
    
    # One-hot encoding for categorical variables
    categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    X_encoded = pd.get_dummies(X, columns=categorical_cols)
    
    logger.info(f"Preprocessed data: {X_encoded.shape}")
    return X_encoded, y

def train_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """Train Random Forest model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info("\nClassification Report:")
    logger.info(classification_report(y_test, y_pred))
    
    return model, scaler, X.columns.tolist()

def save_model(model, scaler, columns, output_path: str):
    """Save trained model and metadata"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save model artifact
    artifact = {
        'model': model,
        'scaler': scaler,
        'columns': columns
    }
    
    joblib.dump(artifact, output_path)
    logger.info(f"Model saved to: {output_path}")

def main():
    """Main training function"""
    # Paths
    data_path = "data/raw/heart.csv"
    output_path = "data/processed/model.pkl"
    
    try:
        # Load data
        logger.info("Loading data...")
        data = load_data(data_path)
        
        # Preprocess data
        logger.info("Preprocessing data...")
        X, y = preprocess_data(data)
        
        # Train model
        logger.info("Training model...")
        model, scaler, columns = train_model(X, y)
        
        # Save model
        logger.info("Saving model...")
        save_model(model, scaler, columns, output_path)
        
        logger.info("✅ Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during model training: {e}")
        raise

if __name__ == "__main__":
    main()
