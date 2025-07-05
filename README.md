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
git clone https://github.com/your-username/github-anomaly-project.git
cd github-anomaly-project
pipenv install --dev
pipenv shell
