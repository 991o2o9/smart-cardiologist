from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Heart Risk API")

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка модели
artifact = joblib.load("model.pkl")
model = artifact["model"]
COLUMNS = artifact["columns"]

class HeartData(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int
    pulse: int

@app.post("/predict")
def predict(data: HeartData):
    input_dict = data.dict()
    df = pd.DataFrame([input_dict])
    df = pd.get_dummies(df)
    df = df.reindex(columns=COLUMNS, fill_value=0)

    pred = model.predict(df)[0]
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(df)[:, 1][0])
    else:
        prob = float(pred)

    return {"risk": int(pred), "probability": round(prob, 4)}
