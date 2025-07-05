from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from pathlib import Path

app = FastAPI()

MODEL_PATH = Path("models/isolation_forest.pkl")

# Load model
try:
    loaded = joblib.load(MODEL_PATH)
    if isinstance(loaded, tuple) and len(loaded) == 2:
        scaler, model = loaded
    else:
        raise ValueError("Expected a (scaler, model) tuple in model file.")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    model = None
    scaler = None


# Define request schema
class FeatureInput(BaseModel):
    features: list[float]


# Health check
@app.get("/")
def health_check():
    return {"message": "GitHub Anomaly Detection API is live."}


# Prediction endpoint
@app.post("/predict")
def predict(request: FeatureInput):
    try:
        if model is None or scaler is None:
            raise RuntimeError("Model or scaler not loaded.")

        X = np.array(request.features).reshape(1, -1)
        X_scaled = scaler.transform(X)
        score = model.decision_function(X_scaled)[0]
        return {"anomaly_score": float(score)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
