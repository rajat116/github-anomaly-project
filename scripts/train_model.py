# scripts/train_model.py

import pandas as pd
import numpy as np
import joblib
import mlflow
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Config
input_file = "data/features/actor_features_2024-01-01-15.parquet"
model_dir = Path("models")
model_dir.mkdir(exist_ok=True)
model_file = model_dir / "isolation_forest.pkl"
experiment_name = "anomaly_detection_github"

# Load data
df = pd.read_parquet(input_file)
features = [
    "event_count", "pr_count", "issue_open_count",
    "fork_count", "repo_diversity"
]
X = df[features].fillna(0)

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# MLflow setup
mlflow.set_experiment(experiment_name)
with mlflow.start_run():
    mlflow.log_param("model_type", "IsolationForest")
    mlflow.log_param("n_estimators", 100)
    
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)

    df["anomaly_score"] = model.decision_function(X_scaled)
    df["anomaly"] = model.predict(X_scaled) == -1

    # Save model
    joblib.dump((scaler, model), model_file)
    mlflow.log_artifact(str(model_file))

    print(df[["actor", "anomaly_score", "anomaly"]].head())

    # Optional: Save predictions
    df.to_parquet("data/features/actor_predictions_2024-01-01-15.parquet", index=False)
    mlflow.log_artifact("data/features/actor_predictions_2024-01-01-15.parquet")
