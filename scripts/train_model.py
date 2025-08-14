import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

def train_model():
    """Обучить модель"""
    try:
        print("🤖 Обучение ML модели...")
        
        # Пути к файлам
        data_path = project_root / "data" / "raw" / "heart.xls"
        model_path = project_root / "data" / "processed" / "model.pkl"
        
        # Создаем директорию если не существует
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. Загрузка данных
        print("📊 Загрузка данных...")
        if not data_path.exists():
            raise FileNotFoundError(f"Файл данных не найден: {data_path}")
        
        df = pd.read_csv(data_path)
        print(f"   Загружено {len(df)} записей")
        
        # 2. Добавляем pulse, если нет
        if "pulse" not in df.columns:
            print("   Добавление колонки pulse...")
            df["pulse"] = np.random.randint(60, 110, size=len(df))
        
        # 3. Проверяем наличие целевой колонки
        if "target" not in df.columns:
            raise ValueError("В датасете нет колонки 'target'")
        
        # 4. Подготовка данных
        print("🔧 Подготовка данных...")
        X = df.drop(columns=["target"])
        y = df["target"]
        
        # One-hot encoding
        X = pd.get_dummies(X)
        print(f"   Количество признаков: {X.shape[1]}")
        
        # 5. Разбивка на train/test
        print("📈 Разбивка на train/test...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print(f"   Train: {len(X_train)} записей")
        print(f"   Test: {len(X_test)} записей")
        
        # 6. Обучение модели
        print("🎯 Обучение модели...")
        model = RandomForestClassifier(
            n_estimators=200, 
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # 7. Оценка модели
        print("📊 Оценка модели...")
        y_pred = model.predict(X_test)
        
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        try:
            roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
            print(f"🎯 ROC AUC: {roc_auc:.4f}")
        except:
            print("⚠️  ROC AUC недоступен")
        
        # 8. Сохранение модели
        print("💾 Сохранение модели...")
        artifact = {
            "model": model,
            "columns": X.columns.tolist()
        }
        joblib.dump(artifact, model_path)
        print(f"   Модель сохранена: {model_path}")
        
        # 9. Информация о модели
        print("\n📋 Информация о модели:")
        print(f"   Тип: {type(model).__name__}")
        print(f"   Признаков: {len(X.columns)}")
        print(f"   Деревьев: {model.n_estimators}")
        print(f"   Точность на тесте: {(y_pred == y_test).mean():.4f}")
        
        print("\n✅ Обучение завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при обучении модели: {e}")
        sys.exit(1)

if __name__ == "__main__":
    train_model()
