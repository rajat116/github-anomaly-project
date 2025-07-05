# 🛠️ GitHub Anomaly Detection Pipeline

A production-grade anomaly detection system for GitHub user behavior using:

- **Apache Airflow** for orchestration  
- **Isolation Forest** for anomaly detection  
- **FastAPI** for real-time inference  
- **Pytest, Black, Flake8** for testing and linting  
- **CI/CD with GitHub Actions**  
- **Streamlit UI (optional)** for visualization

---

## 📦 Project Structure

github-anomaly-project/
├── dags/ # Airflow DAGs
├── github_pipeline/ # Ingestion, feature engineering, inference
├── models/ # Saved ML model and scaler
├── scripts/ # One-off runnable scripts
├── tests/ # Pytest-based unit tests
├── Dockerfile.inference # For FastAPI deployment
├── docker-compose.yaml # Airflow setup
├── requirements.txt # Python packages
├── serve_model.py # FastAPI inference app
├── .pre-commit-config.yaml # Black + Flake8 hooks
├── Pipfile / Pipfile.lock # Pipenv environment
└── README.md

