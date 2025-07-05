from fastapi.testclient import TestClient
from serve_model import app
import warnings

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but StandardScaler was fitted with feature names",
)

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GitHub Anomaly Detection API is live."}


def test_predict_valid():
    response = client.post("/predict", json={"features": [0.5, 0.3, 0.1, 0.0, 0.8]})
    assert response.status_code == 200
    assert "anomaly_score" in response.json()


def test_predict_invalid_input():
    response = client.post("/predict", json={"invalid": "data"})
    assert response.status_code == 422  # Unprocessable Entity (schema mismatch)


def test_predict_missing_model(monkeypatch):

    # Temporarily break the model and scaler
    monkeypatch.setattr("serve_model.model", None)
    monkeypatch.setattr("serve_model.scaler", None)

    response = client.post("/predict", json={"features": [0.1] * 5})
    assert response.status_code == 400
    assert "Model or scaler not loaded" in response.json()["detail"]
