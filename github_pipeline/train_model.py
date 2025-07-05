# github_pipeline/train_model.py

import argparse
import pandas as pd
import joblib
import mlflow
from pathlib import Path
from glob import glob
import re
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def run_training(timestamp: str):
    print("[INFO] Starting model training...")

    input_file = f"data/features/actor_features_{timestamp}.parquet"
    output_file = f"data/features/actor_predictions_{timestamp}.parquet"
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    model_file = model_dir / "isolation_forest.pkl"
    experiment_name = "anomaly_detection_github"

    if not Path(input_file).exists():
        raise FileNotFoundError(f"[ERROR] Input file not found: {input_file}")

    # Load features
    df = pd.read_parquet(input_file)
    features = [
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    ]
    X = df[features].fillna(0)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # MLflow experiment
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run():
        mlflow.log_param("timestamp", timestamp)
        mlflow.log_param("model_type", "IsolationForest")
        mlflow.log_param("n_estimators", 100)

        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        model.fit(X_scaled)

        # Predict
        df["anomaly_score"] = model.decision_function(X_scaled)
        df["anomaly"] = model.predict(X_scaled) == -1

        # Save model and scaler
        joblib.dump((scaler, model), model_file)
        mlflow.log_artifact(str(model_file))

        # Save timestamp of training
        with open(model_dir / "last_trained.txt", "w") as f:
            f.write(timestamp)

        # Save predictions
        df.to_parquet(output_file, index=False)
        mlflow.log_artifact(output_file)

        print(df[["actor", "anomaly_score", "anomaly"]].head())

    print("[INFO] Training completed successfully.")


def main():
    # Automatically detect latest timestamp
    files = glob("data/features/actor_features_*.parquet")
    if not files:
        raise FileNotFoundError("[ERROR] No actor feature parquet files found.")

    # Extract timestamps
    timestamps = []
    for f in files:
        match = re.search(r"actor_features_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet", f)
        if match:
            timestamps.append(match.group(1))

    if not timestamps:
        raise RuntimeError("[ERROR] No valid timestamps parsed from filenames.")

    latest_ts = sorted(timestamps)[-1]
    print(f"[INFO] Found latest timestamp: {latest_ts}")
    run_training(latest_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timestamp",
        help="Format: YYYY-MM-DD-HH. If not set, uses latest available file.",
    )
    args = parser.parse_args()

    if args.timestamp:
        run_training(args.timestamp)
    else:
        main()
