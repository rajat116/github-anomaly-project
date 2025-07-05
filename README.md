# 🛠️ GitHub Anomaly Detection Pipeline

A production-grade anomaly detection system for GitHub user behavior using:

- **Apache Airflow** for orchestration  
- **Pandas + Scikit-learn (Isolation Forest)** for modeling and anomaly detection
- **FastAPI** for real-time inference  
- **Pytest, Black, Flake8** for testing and linting  
- **Pre-commit + GitHub Actions** for CI/CD and code quality 
- **Streamlit UI (optional)** for visualization

---

## 📦 Project Structure

# To Do


---

## 📈 Use Case

The pipeline detects anomalies in GitHub user behavior on an hourly basis and can:

- Alert on suspicious activity (e.g., bot-like behavior)
- Serve anomaly scores via API
- Continuously retrain and monitor model health

---

## ⚙️ Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/rajat116/github-anomaly-project.git
cd github-anomaly-project
pipenv install --dev
pipenv shell
```
### Or install using pip:

```bash
pip install -r requirements.txt
```

### 2. Run Airflow with Docker Compose

#### Build and start Airflow:

```bash
docker compose build airflow
docker compose up airflow
```

Then go to:

```bash
http://localhost:8080
```
Login: airflow / airflow

#### ⏱️ Airflow DAGs

daily_github_inference: Download → Feature Engineering → Inference
daily_monitoring_dag: Drift checks, cleanup, alerting
retraining_dag: Weekly model retraining

### 🧠 Model Training

The model (Isolation Forest) is trained on actor-wise event features:

```bash
python scripts/train_model.py
```
The latest parquet file is used automatically. Model and scaler are saved to models/.

### 🚀 FastAPI Inference

#### Build & Run

```bash
docker build -t github-anomaly-inference -f Dockerfile.inference .
docker run -p 8000:8000 github-anomaly-inference
```

#### Test the API

```bash
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"features": [12, 0, 1, 0, 4]}'
```

### ✅ CI/CD with GitHub Actions

The .github/workflows/ci.yml file runs on push:

    ✅ black --check
    ✅ flake8 (E501 ignored)
    ✅ pytest
    ✅ (optional) Docker build

### 🔍 Code Quality

Pre-commit hooks ensure style and linting:

```bash
pre-commit install
pre-commit run --all-files
```

Configured via:

    .pre-commit-config.yaml
    .flake8 (ignore = E501)

### 🧪 Testing

Run all tests:

```bash
PYTHONPATH=. pytest
```

Tests are in tests/ and cover:

    Inference API (serve_model.py)
    Feature engineering
    Model training logic

### 📊 Optional Streamlit Dashboard

You can optionally add a Streamlit UI to:

    Show anomaly scores
    Display drift metrics
    Visualize last 24h user activity

Great for demos and storytelling.

### 🧭 Architecture

To Do

[GitHub Archive Logs]
       ↓
[Airflow DAG]
       ↓
[Feature Engineering]
       ↓
[Isolation Forest Model]
       ↓           ↘
[API: FastAPI]    [Alerts / Drift Monitor]

### 🧹 Clean Code

All code follows:

    PEP8 formatting via Black
    Linting with Flake8 + Bugbear
    Pre-commit hook enforcement

### 🙌 Credits

Built by Rajat Gupta as part of an MLOps portfolio.
Inspired by real-time event pipelines and anomaly detection architectures used in production.

### 📝 License

MIT License