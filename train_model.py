import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# 1. Загрузка
df = pd.read_csv("heart.xls")

# 2. Добавляем pulse, если нет
if "pulse" not in df.columns:
    df["pulse"] = np.random.randint(60, 110, size=len(df))

# 3. Простая предобработка (пример — подстрой под свой датасет)
# Убедись, что целевая колонка называется "target"
assert "target" in df.columns, "В датасете нет колонки 'target'"

X = df.drop(columns=["target"])
y = df["target"]

# Если есть категориальные — можно one-hot (но сохраняй порядок колонок)
X = pd.get_dummies(X)

# 4. Разбивка
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Обучение
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 6. Оценка
pred = model.predict(X_test)
print(classification_report(y_test, pred))
try:
    print("ROC AUC:", roc_auc_score(y_test, model.predict_proba(X_test)[:,1]))
except:
    pass

# 7. Сохранение: сохраняем и модель, и список колонок
artifact = {"model": model, "columns": X.columns.tolist()}
joblib.dump(artifact, "model.pkl")
print("Saved model.pkl")
