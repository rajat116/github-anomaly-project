# 🛠️ GitHub Anomaly Detection Pipeline

A production-grade anomaly detection system for GitHub user behavior using:

- **Apache Airflow** for orchestration  
- **Pandas + Scikit-learn (Isolation Forest)** for modeling and anomaly detection
- **Alerts: Email & Slack** alerting mechanisms for anomaly spikes and data drift
- **FastAPI** for real-time inference  
- **Pytest, Black, Flake8** for testing and linting  
- **Pre-commit + GitHub Actions** for CI/CD and code quality 
- **Streamlit UI** for visualization

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

- daily_github_inference: Download → Feature Engineering → Inference
- daily_monitoring_dag: Drift checks, cleanup, alerting
- retraining_dag: Weekly model retraining

### 🧠 Model Training

The model (Isolation Forest) is trained on actor-wise event features:

```bash
python scripts/train_model.py
```
The latest parquet file is used automatically. Model and scaler are saved to models/.

### 🚀 3. FastAPI Inference

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

### 5. 📣 Alerts: Email & Slack

This project includes automated alerting mechanisms for anomaly spikes and data drift, integrated into the daily_monitoring_dag DAG.

#### ✅ Triggers for Alerts

- 🔺 Anomaly Rate Alert: If anomaly rate exceeds a threshold (e.g. >10% of actors).
- 🔁 Drift Detection Alert: If feature distributions change significantly over time.

#### 🔔 Notification Channels

- Email alerts (via smtplib)
- Slack alerts (via Slack Incoming Webhooks)

#### 🔧 Configuration

Set the following environment variables in your Airflow setup:

```bash
# .env or Airflow environment
ALERT_EMAIL_FROM=your_email@example.com
ALERT_EMAIL_TO=recipient@example.com
ALERT_EMAIL_PASSWORD=your_email_app_password
ALERT_EMAIL_SMTP=smtp.gmail.com
ALERT_EMAIL_PORT=587

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```
🛡️ Email app passwords are recommended over actual passwords for Gmail or Outlook.

#### 📁 Alert Script

Logic is handled inside:

```bash
github_pipeline/monitor.py
alerts/alerting.py
```

These generate alert messages and send them through email and Slack if thresholds are breached.

### 4. ✅ CI/CD with GitHub Actions

The .github/workflows/ci.yml file runs on push:

- ✅ black --check
- ✅ flake8 (E501,W503 ignored)
- ✅ pytest
- ✅ (optional) Docker build

### 🔍 Code Quality

Pre-commit hooks ensure style and linting:

```bash
pre-commit install
pre-commit run --all-files
```

Configured via:

- .pre-commit-config.yaml
- .flake8 (ignore = E501)

### 4. 🧪 Testing

Run all tests:

```bash
PYTHONPATH=. pytest
```

Tests are in tests/ and cover:

- Inference API (serve_model.py)
- Feature engineering
- Model training logic

### 6. 📊 Streamlit Dashboard

The project includes an optional interactive Streamlit dashboard to visualize:

- ✅ Latest anomaly predictions
- 📈 Data drift metrics from the Evidently report
- 🧑‍💻 Top actors based on GitHub activity
- ⏱️ Activity summary over the last 48 hours

#### 🔧 How to Run Locally

Make sure you have installed all dependencies via Pipenv, then launch the Streamlit app:

```bash
pipenv run streamlit run streamlit_app.py
```

Once it starts, open the dashboard in your browser at:

```bash
http://localhost:8501
```

The app will automatically load:

- The latest prediction file from data/features/
- The latest drift report from reports/

Note: If these files do not exist, the dashboard will show a warning or empty state. You can generate them by running the Airflow pipeline or the monitoring scripts manually.

#### 🐳 Optional: Run via Docker

You can also build and run the dashboard as a container (if desired):

Build the image:

```bash
docker build -t github-anomaly-dashboard -f Dockerfile.streamlit .
```

Run the container:

```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  github-anomaly-dashboard
```

Then open your browser at http://localhost:8501.

### 7. 🧭 Architecture

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

### 8. 🧹 Clean Code

All code follows:

- PEP8 formatting via Black
- Linting with Flake8 + Bugbear
- Pre-commit hook enforcement

### 9. 🙌 Credits

Built by Rajat Gupta as part of an MLOps portfolio.
Inspired by real-time event pipelines and anomaly detection architectures used in production.

### 10. 📝 License

MIT License